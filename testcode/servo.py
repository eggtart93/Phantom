import wiringpi2 as wiringpi

SERVO_PIN = 12

class ServoManager(object):

	def __init__(self):
        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(SERVO_PIN,2)
        wiringpi.pwmSetMode(0)
        wiringpi.pwmSetClock(375)
        angle = 90
        dutyCycle = int(angle/180.0*(0.14*1024)) + 6
        wiringpi.pwmWrite(SERVO_PIN,dutyCycle)

    def servoturn(self,angle):
        dutyCycle = int(angle/180.0*(0.14*1024)) + 6
        wiringpi.pwmWrite(SERVO_PIN,dutyCycle)
