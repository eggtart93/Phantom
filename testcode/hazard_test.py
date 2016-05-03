#!/usr/bin/python
# gpio_managers.py

import sys, time, logging, threading
from config import *

logging.basicConfig(level=logging.DEBUG,
        #filename=APP_LOGFILE,
        #filemode='w'
        format='[%(levelname)5s](%(threadName)-s) %(message)s',
        )

global movement
motorSpeed = MOTOR_SPEED_ZERO
obstacleDetected = False
condition = False
movement = 0

def calculate_movement():
    global motorSpeed
    global movement
    movement += motorSpeed
    return movement

def calculate_safe_dist():
    global motorSpeed
    return MIN_SAFE_DISTANCE + motorSpeed * motorSpeed * SPD_EFFECT

def hazard_detected():
    global obstacleDetected
    return obstacleDetected

class MotorState:
    Off, Stop, Forward, Backward, LeftTurn, RightTurn = range(6)

class MotorManager(object):
    """ This class is used to drive the DC motors """

    def __init__(self):
        # Warm up motors
        self.currentState = MotorState.Off
        logging.info("Initializes Engine Completed.")

    def start(self):
        self.currentState = MotorState.Stop
        logging.info("Engine starts.")

    def set_speed(self, speed):
        global motorSpeed
        motorSpeed = speed
        logging.debug("speed set to %d", speed)

    def move_forward(self, speed=MOTOR_SPEED_DEFAULT):
        global obstacleDetected
        if not obstacleDetected:
            self.set_speed(speed)
            self.currentState = MotorState.Forward
            logging.debug("move_forward: motors set.")

    def move_backward(self, speed=MOTOR_SPEED_DEFAULT):
        self.set_speed(speed)
        self.currentState = MotorState.Backward
        logging.debug("move_backward: motors set.")

    def turn_left(self, speed=MOTOR_SPEED_DEFAULT):
        self.set_speed(speed)
        self.currentState = MotorState.LeftTurn
        logging.debug("turn_left: motors set.")

    def turn_right(self, speed=MOTOR_SPEED_DEFAULT):
        self.set_speed(speed)
        self.currentState = MotorState.RightTurn
        logging.debug("turn_right: motors set.")

    def stop_movement(self):
        self.set_speed(MOTOR_SPEED_ZERO)
        self.currentState = MotorState.Stop
        logging.debug("stop_movement: motors set.")

    def shutdown(self):
        logging.warning("Engine has been shutdown.")


class UltrasonicManager(object):
    """ Use ultrasonic sensor to detect obstacle """

    def __init__(self, hazardHandler):
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

    def detect_obstacle(self):
        logging.info("Obstacle Detection Starts...")
        global condition
        global obstacleDetected
        logEn = False
        distance = 0
        while self.running:
            isTimeout = False
            # Generate 10us pulse to trigger
            time.sleep(ULTRASONIC_PULSE_DURATION)

            expired = time.time() + ULTRASONIC_READ_TIMEOUT
            while condition:
                if time.time() >= expired:
                    logging.warning("Ultrasonic Sensor Timeout. 1")
                    isTimeout = True
                    break
            if isTimeout: continue

            # Signal becomes high, Pulse arrived
            pulseStart = time.time()

            expired = pulseStart + ULTRASONIC_READ_TIMEOUT
            while condition:
                if time.time() >= expired:
                    logging.warning("Ultrasonic Sensor Timeout. 2")
                    isTimeout = True
                    break
            if isTimeout: continue

            # Signal becomes low, Pulse died
            pulseEnd = time.time()

            # Calculate Distance to Obstacle
            # Distance pulse travelled = time travelled * the speed of sound (34300 cm/s)
            # Distance to obstacle = Distance pulse travelled / 2
            # Thus, Distance to obstacle = 0.5 * (time travelled * the speed of sound)
            distance = 500.0 - calculate_movement()

            # Threshold distance is changed base on the speed of the car
            threshold = calculate_safe_dist()

            if distance <= threshold:

                obstacleDetected = True
                if logEn:
                    self.hazardHandler()
                    logEn = False
                    logging.debug("Threshold:%d\tDetected:%d", threshold, distance)
            else:
                obstacleDetected = False
                logEn = True

            # set refresh rate to 120Hz~ (0.0083 sec)
            time.sleep(0.008)
        logging.warning("Obstacle detection Stopped.")

    def shutdown(self):
        self.running = False
        if self.backgroundTask and self.backgroundTask.isAlive():
            self.backgroundTask.join()
        logging.warning("Ultrasonic Sensor has been shutdown.")

if __name__ == '__main__':
    motorMgr = MotorManager()
    ultrasonicMgr = UltrasonicManager(motorMgr.stop_movement)
    try:
        motorMgr.start()
        ultrasonicMgr.start()
        motorMgr.move_forward()
        warningSent = False
        while True:
            time.sleep(1)
            if hazard_detected():
                if not warningSent:
                    warningSent = True
                    logging.warning("Hazard Detected!")
                    time.sleep(2)
                    movement = 0
            else:
                warningSent = False

    except KeyboardInterrupt:
        logging.warning("Keyboard Interrupt")
        motorMgr.shutdown()
        ultrasonicMgr.shutdown()
        #os._exit(1)
    else:
        network.shutdown()
        logging.info("Normal Exit")
