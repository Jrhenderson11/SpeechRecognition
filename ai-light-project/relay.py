#!/usr/bin/env python3

import socket               # Import socket module
import RPi.GPIO as GPIO
import time
import re

class Connection():
	
	def __init__(self):
		self.s = socket.socket()         
		self.host = socket.gethostname() 
		self.port = 12345 
		self.connected = False
	
	def start_server(self):
		s = self.s
		s.bind(('192.168.0.19', self.port))
		s.listen(5)
		print('listening')
		self.c, addr = s.accept()
		self.connected = True
		print('Got connection from ' + str(addr))
			
	def is_connected(self):
		return self.connected

	def send(self, data):
		self.c.send(data)
	
	def recieve(self):
		data = self.c.recv(1024)
		return data

	def close(self):
		self.c.close()

# listens over network for instructions to turn on or off
def run_as_server():
	server = Connection()
	print(" Server started listening on " + str(server.host) + " : " + str(server.port))
	server.start_server()
	data = re.findall(r'(?<=b\').*(?=\\n\')', str(server.recieve()))[0]
	print("recieved: " + data)
	while not data=="quit":
		if data == "on":
			turn_on()
		elif data == "off":
			turn_off()
		data = re.findall(r'(?<=b\').*(?=\\n\')', str(server.recieve()))[0]
		print(data)
	print(" Server quitting")
	server.close()

def setup():
	GPIO.setmode(GPIO.BCM)

	pinList = [2,3]

	for pin in pinList:
		GPIO.setup(pin, GPIO.OUT)

def turn_on():
	GPIO.output(2, GPIO.LOW)
	time.sleep(0.1)
	GPIO.output(2, GPIO.HIGH)
	print("On")

def turn_off():
	GPIO.output(3, GPIO.LOW)
	time.sleep(0.1)
	GPIO.output(3, GPIO.HIGH)	
	print("Off")

def test():
	turn_on()
	time.sleep(3)
	turn_off()	

if __name__ == "__main__":
	setup()
	try:
		run_as_server()
	except:
		print("error")
	#	finally:
	#		GPIO.cleanup()
	GPIO.cleanup()