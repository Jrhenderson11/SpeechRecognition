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
		self.s.close()

# listens over network for instructions to turn on or off
def run_as_server():
	on = False
	server = Connection()
	print(" Server started listening on " + str(server.host) + " : " + str(server.port))
	server.start_server()
	data = server.recieve()
	print(data)
	data = re.findall(r'(?<=b\').*(?=\')', str(data))[0]
	data = re.sub(r"\\n", "", data)
	print("recieved: " + data)
	while not data=="quit":
		if data == "on" and on==False:
			turn_on()
			on = True
		elif data == "off" and on==True:
			turn_off()
			on = False
		data = re.findall(r'(?<=b\').*(?=\')', str(server.recieve()))[0]
		data = re.sub(r"\\n", "", data)
		print("recieved: " + data)
		if data == '':
			print("restarting server")
			server.close()
			print("waiting for port to open")
			socketbusy = True
			while socketbusy == True:
				socketbusy = False
				try:
					server = Connection()
					server.start_server()
				except socket.error as e:
					socketbusy = True

			print("restarted")
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
	time.sleep(10)
	try:
		run_as_server()
	except Exception as e:
		print("error: " + str(e))
	GPIO.cleanup()
