#!/usr/bin/python
# config.py

import os.path

class Debug(object):
    DEBUG = True
    HOST = ""
    PORT = 8080
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    # PIN Assignments
    MOTOR_PWM1_IN1_PIN = 18
    MOTOR_PWM2_IN2_PIN = 11

    # Motor settings
    DEFAULT_SPEED = 70
    DEFAULT_ROTATION_SPEED = 200
    SPEED_STEP = 10
