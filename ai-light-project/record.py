#!/usr/bin/env python3
import pyaudio
import socket
import struct
import wave
import math
import sys
import ai
import re
import os

def printgreen(text):
	print('\033[92m' + text + '\033[0m')

def printred(text):
	print('\033[31m' + text + '\033[0m')

# https://stackoverflow.com/questions/4160175/detect-tap-with-pyaudio-from-live-mic/4160733
def get_rms( block ):
	SHORT_NORMALIZE = (1.0/32768.0)
	count = len(block)/2
	format = "%dh"%(count)
	shorts = struct.unpack( format, block )

	sum_squares = 0.0
	for sample in shorts:
		n = sample * SHORT_NORMALIZE
		sum_squares += n*n

	return math.sqrt( sum_squares / count )

# set stuff up for pyAudio
def initialise_audio_params():
	global SPEAKING, BACKGROUND, CHUNK, FORMAT, CHANNELS, RATE, RECORD_SECONDS, WAVE_OUTPUT_FILENAME, p
	p = pyaudio.PyAudio()
	SPEAKING = False
	BACKGROUND = 0.5
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	RATE = 44100
	RECORD_SECONDS = 20
	WAVE_OUTPUT_FILENAME = "output.wav"

# save data to a .wav file 
def save_recording(fname, frames):
	wf = wave.open(fname, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()

# attempt to establish a background noise level
def get_background():
	total = 0
	num = 0 
	
	RECORD_SECONDS = 5
	
	stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		data = stream.read(CHUNK)
		total += get_rms(data)

	avg = total / int(RATE / CHUNK * RECORD_SECONDS)

	printred("* Background level: " + str(avg))

	stream.stop_stream()
	stream.close()
	p.terminate()	
	return avg

def setup_client():
	s = socket.socket()
	host = socket.gethostname()
	port = 12345

	s.connect(('192.168.0.19', port))
	return s

# listen for speech and try to classify words said
def live(connection):
	if connection == True:
		s = setup_client()
	SPEAKING = False
	printgreen("* initialising AI model")
	word_models = ai.build_models("data/")

	stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

	frames = []
	countend = 0

	print("* recording")

	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		data = stream.read(CHUNK)
		if get_rms(data) > BACKGROUND and SPEAKING==False:
			SPEAKING = True
			printgreen("Speaking")

		if get_rms(data) < BACKGROUND and SPEAKING==True:
			if countend < 30:
				countend+=1
			elif countend==0:
				countend = 0
				SPEAKING = False
				printred("End")

				#save recording and analyse
				save_recording("temp.wav", frames)
				frames = []

				#wot i fink u said
				label = ai.classify("temp.wav", word_models)
				printgreen("Result: " + label)
				if connection == True:
					print("sending " + label + " to server")
					s.send(label.encode())

		if SPEAKING==True:
			frames.append(data)

	print("* done recording")

	stream.stop_stream()
	stream.close()
	p.terminate()
	if connection == True:
		s.close()

def record_samples(word):

	name = "data/" + word + "/" + word
	SPEAKING = False
	stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

	#get num
	maximum = 0
	print(re.findall(r'(.*/)*', name)[0])
	
	for root, directories, file in os.walk(re.findall(r'(.*/)*', name)[0]):
		regex = str("(?<="+ name.split("/")[::-1][0] + ")\d+")
		matches = re.findall(regex, str(file))
		print(matches)
		for match in matches:
			num = int(match)
			if num > maximum:
				maximum = num

	recordings = maximum + 1
	printgreen("Set recordings to " + str(recordings))

	frames = []
	countend = 0

	printred("* recording word " + word)

	while True:
		data = stream.read(CHUNK)
		if get_rms(data) > BACKGROUND and SPEAKING==False:
			SPEAKING = True
			printgreen("Speaking")

		# if finished speaking wait a bit and then finish the recording
		if get_rms(data) < BACKGROUND and SPEAKING==True:
			if countend < 30:
				countend+=1
			else:
				countend = 0
				SPEAKING = False
				printred("End")
				save_recording(name + str(recordings) + ".wav", frames)
				recordings+=1
				#reset frames
				frames = []
		if SPEAKING==True:
			frames.append(data)

	printred("* done recording")

	stream.stop_stream()
	stream.close()
	p.terminate()

if __name__=='__main__':

	args = sys.argv[1:]
	initialise_audio_params()
	try:
		#record_samples("on")
		live(True)
	except KeyboardInterrupt as e:
		print("quitting")

#TODO: 
# - set get_background to return std deviation
# - multiple word splitting
