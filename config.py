#!/usr/bin/python
# config.py

import os.path

# ========== General ==========
APP_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_LOGFILE = "phantom.log"

# ========== Network ==========
NETWORK_HOST = ""
NETWORK_PORT = 8080
NETWORK_TIMEOUT = 3
NETWORK_BUFFER_SIZE = 2048

# ========== GPIO PINS ASSIGNMENT ==========
# DC Motors
MOTOR_LEFT_EN_O_PIN = 19
MOTOR_LEFT_DIR_O_PIN = 22
MOTOR_RIGHT_EN_O_PIN = 11
MOTOR_RIGHT_DIR_O_PIN = 7
# Ultrasonic Sensor
ULTRASONIC_TRIG_O_PIN = 21
ULTRASONIC_ECHO_I_PIN = 23
COLLISION_WARNING_I_PIN=24
COLLISION_WARNING_O_PIN = 26
# Servo
SERVO_PIN = 12

# ========== Global Constants ==========
MOTOR_SPEED_HIGH = 100
MOTOR_SPEED_DEFAULT = 90
MOTOR_SPEED_ZERO = 0
MIN_SAFE_DISTANCE = 5
SPD_EFFECT = 0.002
ULTRASONIC_PULSE_DURATION = 0.00001
ULTRASONIC_READ_TIMEOUT = 0.02
