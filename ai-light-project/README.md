# AI light thingumy

A project that uses a machine learning powered speech recognition to turn a light on and off!

## Description

This started off as a project to just have a light that could be turned off with a raspberry pi, possibly for an IOT project or something, then I began working on some speech recognition and thought it would be nice to try and make the light turn on and off with my voice. I tried some of the examples in the .. folder in voice.py like using Google speech recognition API or sphinx. The sphinx version wasn't any good and the google one was good, but because it involved a web request it was a bit slow, even half a second of delay is noticable with speech recognition.

Then I got a load of books on artificial intelligence and machine learning from humble-bundle, and one of the books had a chapter which was a guide to building a speech recognition system with machine learning using hidden markov models, so I followed that to make ai.py and then combined that with pyAudio's ability to lsiten to a microphone and save the result to a .wav file to make a system that can translate microphone input.


## File overview:

 - **hmm-speech-recognition-0.1/** a folder containing utilities for speech recognition using hidden markov models and some sample testing data (in the `audio/` folder)

 - **data/** This is where the training / testing data for the speech recognition is stored, currently it's empty because I don't really feel like uploading 150 samples of my voice for the public domain, but for the system to work it will need to contain practice audio data. Basically each word you want the ai to learn should be in a subfolder of data called the wordname filled with .wav files e.g `data/on/on.wav`. The system will use the folder name to train the meaning of the wav files, so it doesn't matter what they're called but it's useful to call them `on01.wav ... on50.wav`

 - **ai.py** This is the python script for building, training and testing a model to interpret speech data and classify audio samples. The main method can be set to either run tests over the whole batch of input data or just query the classification for certain files

 - **record.py** This file has all the audio stuff for recording live audio, detecting that someone is speaking, recording samples and also currently works as the interface to the system

 - **relay.py** Some sample code for turning a light on and off on a raspberry pi, this might be different to the expected implementation, because the particular light I am working with actually has an inbuilt AC adapter and short circuit protection so requires 2 relays to turn on and off nicely (one in series and one in parrallel) 


## Training:

The system works by training a machine learning model to differentiate between different words. This is done by feeding a hidden markov model with labelled data, and testing to see how well it is able to differentiate between the samples. This is a classification system, given an audio sample the machine decides which category it should be categorised as belonging to. Here is a quick overview of machine learning training tips for classification problems:

 - give the sytem enough data to learn from, this is especially important if the variation is subtle between the classifications (I used ~ 50 samples of each word for **on** and **off**)

 - give an equal amount of training data for each class, if not the system may have a bias to the data you provided more data for

 - make sure the input data is representative of the data the system will be run on when live / testing, e.g. if your speech recognition is done with an omnidirectional microphone in a noisy room then don't just train using a headset microphone with low noise

 **BUT ALSO**

 - make sure your training data is varied, other wise you will have the problem of **overfitting** where it will distinguish between subtle variations in the same class as belonging to separate classifications. This is also associated with the amount of data used to train (too much data can lead to overfitting without enough variation). an example of this would be a speech recognition system trained too much on one accent only, and not recognising other peoples voices


**How to perform the training:**

This system gets all its training data from the folder `data/` (but you could change this in the source code). In the `data/` folder should be a number of subfolders, each subfolder is one word and contains a lot of wav files of that word, here's a diagram:

```
data ---|-----> on ---| on01.wav ... on50.wav
		|
		|-----> on ---| off01.wav ... off50.wav
		|
		|-----> light ---| light01.wav ... light50.wav
```

You can also find a sample set up with some placeholder wav files in `hmm-speech-recognition-0.1/audio/` (imagine this is a data folder equivalent). Notice how this data is not enough to reliably distinguish.

50 samples per word is quite a bit (I didn't actually see if there was a number below this which worked because I accidentally had uneven amounts of training data until I got up to 50 samples). Especially if you do it how I started like I did, by recording one track of me saying something 10 times and manually splitting and saving each word from audacity. 

Because this is such a pain in the arse I made a short script to automate this process, this is the **record_samples** in record.py. What it does is to capture a stream of mocrophone input, and for each chunk of data (representative of a tiny amount of time) calculates the amplitude of the sound using the root-mean-square. If this is above a predefined variable **BACKGROUND** it starts actually recording the microphone input until the amplitude drops again (it waits so it captures a little more time than exactly the microsecond you stop speaking, this helps capture hyphenated words or phrases of 2 or 3 words). Then it saves this to a wav file. This is designed so you give it a word to label the recordings as, and keep saying the word 

(**WARNING: When the green *Speaking* alert appears this means it is recording, only say one word until it says *End* in red, everything between these 2 points is one file**)

It automates the file saving to look for files in the format `wordNUMBER.wav` e.g `on49.wav`, and knows to save new samples at the next greatest number like `on50.wav` (it only looks at the maximum, it won't fill gaps if you delete files). This means that to record audio you just give it the required word, start the system and keep speaking in between the green and red text, and it will record samples until you stop it.

You might want to calibrate the background level, I tried to make a method that gets the mean but that doesn't give a good value to use as background, I might do it so it finds the mean + >2 standard deviations but that might cut off the first part of the word if you don't speak loud enough.

This should be an easy way to quickly generate enough samples for training. 

## Technical stuff:


