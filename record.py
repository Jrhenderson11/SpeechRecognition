#!/usr/bin/env python3
import pyaudio
import struct
import wave
import math
import ai

def printgreen(text):
	print('\033[92m' + text + '\033[0m')

def printred(text):
	print('\033[31m' + text + '\033[0m')

#https://stackoverflow.com/questions/4160175/detect-tap-with-pyaudio-from-live-mic/4160733
def get_rms( block ):
	SHORT_NORMALIZE = (1.0/32768.0)
	# RMS amplitude is defined as the square root of the 
	# mean over time of the square of the amplitude.
	# so we need to convert this string of bytes into 
	# a string of 16-bit samples...

	# we will get one short out for each 
	# two chars in the string.
	count = len(block)/2
	format = "%dh"%(count)
	shorts = struct.unpack( format, block )

	# iterate over the block.
	sum_squares = 0.0
	for sample in shorts:
		# sample is a signed short in +/- 32768. 
		# normalize it to 1.0
		n = sample * SHORT_NORMALIZE
		sum_squares += n*n

	return math.sqrt( sum_squares / count )


def save_recording(p, fname, chunk_size, rate, format, frames):
	wf = wave.open(fname, 'wb')
	wf.setnchannels(2)
	wf.setsampwidth(p.get_sample_size(format))
	wf.setframerate(rate)
	wf.writeframes(b''.join(frames))
	wf.close()

SPEAKING = False
BACKGROUND = 0.4
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 20
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
				channels=CHANNELS,
				rate=RATE,
				input=True,
				frames_per_buffer=CHUNK)

print("* recording")

frames = []
countend = 0
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	data = stream.read(CHUNK)
	if get_rms(data) > BACKGROUND and SPEAKING==False:
		SPEAKING = True
		printgreen("Speaking")

	if get_rms(data) < BACKGROUND and SPEAKING==True:
		if countend < 30:
			countend+=1
		else:
			countend = 0
			SPEAKING = False
			printred("End")
			#save recording and analyse
			save_recording(p, "temp.wav", CHUNK, RATE, FORMAT, frames)
			#reset frames
			frames = []
			#wot i fink u said
			ai.is_it_on_or_off()
			break


	if SPEAKING==True:
		frames.append(data)

print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()


