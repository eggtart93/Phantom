#!/usr/bin/python
# gpio_managers.py

import sys, time, logging, threading
import Queue
import RPi.GPIO as GPIO
import serial
from config import *

class MotorState:
    Off, Stop, Forward, Backward, LeftTurn, RightTurn = range(6)

motorSpeed = MOTOR_SPEED_ZERO
engineState = MotorState.Off
obstacleDetected = False

def init_gpio_pins():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    # Configure DC motors related pins
    GPIO.setup(MOTOR_LEFT_EN_O_PIN, GPIO.OUT)
    GPIO.setup(MOTOR_LEFT_DIR_O_PIN, GPIO.OUT)
    GPIO.setup(MOTOR_RIGHT_EN_O_PIN, GPIO.OUT)
    GPIO.setup(MOTOR_RIGHT_DIR_O_PIN, GPIO.OUT)

    # Configure ultrasonic sensor related pins
    GPIO.setup(ULTRASONIC_TRIG_O_PIN, GPIO.OUT)
    GPIO.setup(ULTRASONIC_ECHO_I_PIN, GPIO.IN)
    GPIO.setup(COLLISION_WARNING_I_PIN, GPIO.IN)
    GPIO.setup(COLLISION_WARNING_O_PIN, GPIO.OUT)
    logging.info("Initializes GPIO Pins Completed.")

def reset_gpio_pins():
    GPIO.cleanup()

def calculate_safe_dist():
    global motorSpeed
    global engineState
    if engineState == MotorState.Forward:
        return MIN_SAFE_DISTANCE + motorSpeed * motorSpeed * SPD_EFFECT
    elif engineState == MotorState.Backward:
        return -1
    else:
        return MIN_SAFE_DISTANCE

def hazard_detected():
    global obstacleDetected
    return obstacleDetected


class MotorManager(object):
    """ This class is used to drive the DC motors """

    def __init__(self):
        # Warm up motors
        self.motorR = GPIO.PWM(MOTOR_RIGHT_EN_O_PIN, 100)
        self.motorL = GPIO.PWM(MOTOR_LEFT_EN_O_PIN, 100)
        engineState = MotorState.Off
        logging.info("Initializes Engine Completed.")

    def start(self):
        self.motorR.start(0)
        self.motorL.start(0)
        engineState = MotorState.Stop
        logging.info("Engine starts.")

    def set_speed(self, speed):
        global motorSpeed
        self.motorL.ChangeDutyCycle(speed)
        self.motorR.ChangeDutyCycle(speed)
        motorSpeed = speed

    def move_forward(self, speed=MOTOR_SPEED_DEFAULT):
        global engineState
        if not hazard_detected():
            GPIO.output(MOTOR_LEFT_DIR_O_PIN, GPIO.LOW)
            GPIO.output(MOTOR_RIGHT_DIR_O_PIN, GPIO.LOW)
            self.set_speed(speed)
            engineState = MotorState.Forward
            logging.debug("move_forward: motors set.")

    def move_backward(self, speed=MOTOR_SPEED_DEFAULT):
        global engineState
        GPIO.output(MOTOR_LEFT_DIR_O_PIN, GPIO.HIGH)
        GPIO.output(MOTOR_RIGHT_DIR_O_PIN, GPIO.HIGH)
        self.set_speed(speed)
        engineState = MotorState.Backward
        logging.debug("move_backward: motors set.")

    def turn_left(self, speed=MOTOR_SPEED_HIGH):
        global engineState
        GPIO.output(MOTOR_LEFT_DIR_O_PIN, GPIO.HIGH)
        GPIO.output(MOTOR_RIGHT_DIR_O_PIN, GPIO.LOW)
        self.set_speed(speed)
        engineState = MotorState.LeftTurn
        logging.debug("turn_left: motors set.")

    def turn_right(self, speed=MOTOR_SPEED_HIGH):
        global engineState
        GPIO.output(MOTOR_LEFT_DIR_O_PIN, GPIO.LOW)
        GPIO.output(MOTOR_RIGHT_DIR_O_PIN, GPIO.HIGH)
        self.set_speed(speed)
        engineState = MotorState.RightTurn
        logging.debug("turn_right: motors set.")

    def stop_movement(self):
        global engineState
        self.set_speed(MOTOR_SPEED_ZERO)
        engineState = MotorState.Stop
        #detection_enable(False)
        logging.debug("stop_movement: motors set.")

    def shutdown(self):
        global engineState
        engineState = MotorState.Off
        if self.motorL:
            self.motorL.stop()
        if self.motorR:
            self.motorR.stop()
        logging.warning("Engine has been shutdown.")


class UltrasonicManager(object):
    """ Use ultrasonic sensor to detect obstacle """

    def __init__(self, hazardHandler):
        # Set trigger to Low
        GPIO.output(ULTRASONIC_TRIG_O_PIN, False)
        # Set Warning Signal to Low
        #GPIO.output(COLLISION_WARNING_O_PIN, False)
        self.backgroundTask = None
        self.running = False
        self.hazardHandler = hazardHandler
        logging.info("Initializes Ultrasonic Sensor Completed.")

    def start(self):
        # Allow ultrasonic sensor to settle
        time.sleep(0.5)
        self.running = True
        self.backgroundTask = threading.Thread(name="USMgrThread",
                                               target=self.detect_obstacle)
        self.backgroundTask.start()
        logging.info("Ultrasonic sensor starts.")

    def detect_obstacle(self):
        logging.info("Obstacle Detection Starts...")
        global obstacleDetected
        hazardFlag = False
        distance = 0
        while self.running:
            isTimeout = False
            # Generate 10us pulse to trigger
            GPIO.output(ULTRASONIC_TRIG_O_PIN,True)
            time.sleep(ULTRASONIC_PULSE_DURATION)
            GPIO.output(ULTRASONIC_TRIG_O_PIN,False)

            expired = time.time() + ULTRASONIC_READ_TIMEOUT
            while GPIO.input(ULTRASONIC_ECHO_I_PIN) == 0:
                if time.time() >= expired:
                    #logging.warning("read pulse positive edge timeout.")
                    isTimeout = True
                    break
            if isTimeout: continue

            # Signal becomes high, Pulse arrived
            pulseStart = time.time()

            expired = pulseStart + ULTRASONIC_READ_TIMEOUT
            while GPIO.input(ULTRASONIC_ECHO_I_PIN) == 1:
                if time.time() >= expired:
                    #logging.warning("read pulse negative edge timeout.")
                    isTimeout = True
                    break
            if isTimeout: continue

            # Signal becomes low, Pulse died
            pulseEnd = time.time()

            # Calculate Distance to Obstacle
            # Distance pulse travelled = time travelled * the speed of sound (34300 cm/s)
            # Distance to obstacle = Distance pulse travelled / 2
            # Thus, Distance to obstacle = 0.5 * (time travelled * the speed of sound)
            distance = 0.5 * ((pulseEnd - pulseStart) * 34300)

            # Threshold distance is changed base on the speed of the car
            threshold = calculate_safe_dist()
            if distance <= threshold:
                obstacleDetected = True
                if not hazardFlag:
                    self.hazardHandler()
                    hazardFlag = True
                    logging.debug("Threshold:%d\tDetected:%d", threshold, distance)
            else:
                obstacleDetected = False
                hazardFlag = False

            # set refresh rate to 120Hz~ (0.0083 sec)
            time.sleep(0.008)

        logging.debug("Exits from detect_obstacle().")

    def shutdown(self):
        self.running = False
        if self.backgroundTask and self.backgroundTask.isAlive():
            self.backgroundTask.join()
        logging.warning("Ultrasonic Sensor has been shutdown.")


class ServoManager(object):

    def __init__(self):
            GPIO.setmode(GPIO.BOARD)
            GPIO.setwarnings(False)
            GPIO.setup(SERVO_PIN,GPIO.OUT)

    def scan(self):
        pwm = GPIO.PWM(SERVO_PIN,50)
        pwm.start(7)
        for i in range(90,0,-1):
            DC = 1/18.*i+2
            pwm.ChangeDutyCycle(DC)
            time.sleep(.05)
        for i in range(0,180):
            DC = 1./18.*(i)+2
            pwm.ChangeDutyCycle(DC)
            time.sleep(.05)
        for i in range(180,90,-1):
            DC = 1/18.*i+2
            pwm.ChangeDutyCycle(DC)
            time.sleep(.05)

    def turn(self,angle=90):   ##angle = [0,180]
        pwm = GPIO.PWM(SERVO_PIN,50)
        pwm.start(7)
        DC = 1/18.*angle+2
        pwm.ChangeDutyCycle(DC)
