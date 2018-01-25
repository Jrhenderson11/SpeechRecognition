#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

import speech_recognition as sr
import RPi.GPIO as GPIO
import time

# obtain audio from the microphone
try:
    r = sr.Recognizer()
except Exception as e:
    print("something wrong with setup")


#set up relay 
relay = 2

GPIO.setmode(GPIO.BCM)
GPIO.setup(relay, GPIO.OUT)
GPIO.output(relay, GPIO.LOW)
on = False

try:
    while True:
        with sr.Microphone() as source:
            print("listening...")
            audio = r.listen(source)

        # recognize speech using Google Speech Recognition
        words = r.recognize_google(audio)
        try:
            print("You said: " + words)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
       
        if ("light" in words):
            if (on):
                GPIO.output(relay, GPIO.LOW)  
                on = False
            else:
                GPIO.output(relay, GPIO.HIGH)
                on = True
except KeyboardInterrupt:
    GPIO.output(relay, GPIO.LOW)
    print("quitting")