import socket               # Import socket module
import RPi.GPIO as GPIO
import time


def turn_on():
	GPIO.output(2, GPIO.LOW)
	time.sleep(0.1)
	GPIO.output(2, GPIO.HIGH)

	print "On"

def turn_off():
	GPIO.output(3, GPIO.LOW)
	time.sleep(0.1)
	GPIO.output(3, GPIO.HIGH)	
	print "Off"

if __name__ == "__main__":
	GPIO.setmode(GPIO.BCM)

	pinList = [2,3]

	for pin in pinList:
		GPIO.setup(pin, GPIO.OUT)

	turn_on()
	time.sleep(3)
	turn_off()

GPIO.cleanup()
