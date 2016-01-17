#!/usr/bin/python
# gpio_managers.py

import sys, time
import RPi.GPIO as GPIO

##GPIO.setmode(GPIO.BOARD)
##GPIO.setwarnings(False)
##
###setup Motor
##GPIO.setup(12,GPIO.OUT)   #12-IN1 Left wheel move Backward
##GPIO.setup(16,GPIO.OUT)   #16-IN2 Left wheel move Forward
##GPIO.setup(18,GPIO.OUT)   #18-EN1 enable Right wheel to move + PWM
##GPIO.setup(11,GPIO.OUT)   #11-EN2 enable Left wheel to move + PWM
##GPIO.setup(13,GPIO.OUT)   #13-IN3 Right wheel move Forward
##GPIO.setup(15,GPIO.OUT)   #15-IN4 Right wheel move Backward
##right_motor=GPIO.PWM(18,100)  #Set Right Motor PWM
##left_motor=GPIO.PWM(11,100)   #Set Left Motor PWM

class MotorManager(object):

    def __init__(self, logger, config):
        self.logger = logger
        self.default_speed = config.DEFAULT_SPEED
        self.default_rotation_speed = config.DEFAULT_ROTATION_SPEED
        # init 2 motors and related GPIO pins
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

#setup Motor
        GPIO.setup(12,GPIO.OUT)   #12-IN1 Left wheel move Backward
        GPIO.setup(16,GPIO.OUT)   #16-IN2 Left wheel move Forward
        GPIO.setup(18,GPIO.OUT)   #18-EN1 enable Right wheel to move + PWM
        GPIO.setup(11,GPIO.OUT)   #11-EN2 enable Left wheel to move + PWM
        GPIO.setup(13,GPIO.OUT)   #13-IN3 Right wheel move Forward
        GPIO.setup(15,GPIO.OUT)   #15-IN4 Right wheel move Backward
        self.right_motor=GPIO.PWM(18,100)  #Set Right Motor PWM
        self.left_motor=GPIO.PWM(11,100)   #Set Left Motor PWM
        
    def move_forward(self, speed=-1):
        if speed <= 0:
            speed = self.default_speed
        self.logger.debug("MotorManager::move_forward(%d)", speed)
        # move car forward at specified speed
        self.right_motor.start(0)
        self.left_motor.start(0)
        self.right_motor.ChangeDutyCycle(speed)
        self.left_motor.ChangeDutyCycle(speed)
        GPIO.output(12,False)
        GPIO.output(16,True)
        GPIO.output(13,True)
        GPIO.output(15,False)
	

    def move_backward(self, speed=-1):
        if speed <= 0:
            speed = self.default_speed
        self.logger.debug("MotorManager::move_backward(%d)", speed)
        # move car backward at specified speed
        self.right_motor.start(0)
        self.left_motor.start(0)        
        self.right_motor.ChangeDutyCycle(speed)
        self.left_motor.ChangeDutyCycle(speed)
        GPIO.output(12,True)
        GPIO.output(16,False)
        GPIO.output(13,False)
        GPIO.output(15,True)
	

    def turn_left(self, speed=-1):
        if speed <= 0:
            speed = self.default_rotation_speed
        self.logger.debug("MotorManager::turn_left(%d)", speed)
        # turn left at specified speed

    def turn_right(self, speed=-1):
        if speed <= 0:
            speed = self.default_rotation_speed
        self.logger.debug("MotorManager::turn_right(%d)", speed)
        # turn right at specified speed

    def stop_movement(self):
        self.logger.debug("MotorManager::stop_movement()")
        # stop the car
        self.right_motor.stop()
        self.left_motor.stop()
        GPIO.output(12,False)
        GPIO.output(16,False)
        GPIO.output(13,False)
        GPIO.output(15,False)
