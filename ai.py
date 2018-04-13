#!/env/python3
import os
import warnings
import numpy as np
from hmmlearn import hmm
import matplotlib.pyplot as plt
from scipy.io import wavfile
from python_speech_features import mfcc, logfbank

def printgreen(text):
	print('\033[92m' + text + '\033[0m')

def printred(text):
	print('\033[31m' + text + '\033[0m')

# Define a class to train the HMM
class ModelHMM(object):
	def __init__(self, num_components=4, num_iter=1000):
		self.n_components = num_components
		self.n_iter = num_iter
		self.cov_type = 'diag'
		self.model_name = 'GaussianHMM'
		self.models = []
		self.model = hmm.GaussianHMM(n_components=self.n_components,covariance_type=self.cov_type, n_iter=self.n_iter)
	
	# 'training_data' is a 2D numpy array where each row is 13-dimensional
	def train(self, training_data):
		np.seterr(all='ignore')
		print(training_data)
		cur_model = self.model.fit(training_data)
		self.models.append(cur_model)
	
	# Run the HMM model for inference on input data
	def compute_score(self, input_data):
		return self.model.score(input_data)
		
# Define a function to build a model for each word
def build_models(input_folder):
	with warnings.catch_warnings():
		warnings.simplefilter('ignore')

		# Initialize the variable to store all the models
		word_models = []
		# Parse the input directory
		for dirname in os.listdir(input_folder):
			# Get the name of the subfolder
			subfolder = os.path.join(input_folder, dirname)
			if not os.path.isdir(subfolder):
				continue
			# Extract the label
			label = subfolder[subfolder.rfind('/') + 1:]
			
			# collected_features stores all the features for one word (label)
			collected_features = np.array([])
			
			# Create a list of files to be used for training
			# We will leave one file per folder for testing
			training_files = [x for x in os.listdir(subfolder) if x.endswith('.wav')][:-1]
			# Iterate through the training files and build the models
			for fname in training_files:
				#Extract fpath
				fpath = os.path.join(subfolder, fname)
				# Read the audio signal from the input file
				sampling_freq, signal = wavfile.read(fpath)
				# Extract the MFCC features
				features_mfcc = mfcc(signal, sampling_freq)
				# Append to the variable collected_features
				
				if len(collected_features) == 0:
					collected_features = features_mfcc
				else:
					if features_mfcc == []:
						print("empty features")
					else:
						#						print(features_mfcc)
						collected_features = np.append(collected_features, features_mfcc, axis=0)
			print(dirname + ": " + str(collected_features))
			model = ModelHMM()
			model.train(collected_features)
			word_models.append((model, label))
			model = None
		return word_models

#give a .wav file, speech model and returns most likely word
def classify(fname):
	print("testing " + fname)
	# Read input file
	sampling_freq, signal = wavfile.read(fname)

	# Extract MFCC features
	features_mfcc = mfcc(signal, sampling_freq)

	# Define variables
	max_score = -float('inf')
	predicted_label = None

	# Run the current feature vector through all the HMM
	# models and pick the one with the highest score
	for possibility in word_models:
		model, label = possibility

		score = model.compute_score(features_mfcc)
		print(label + ": " + str(score))
		if score > max_score:
			max_score = score
			predicted_label = label
	return predicted_label

#run all the testz
def run_tests(test_files, word_models):
	with warnings.catch_warnings():
		warnings.simplefilter('ignore')

		# Classify input data
		correcton = 0
		correctoff = 0
		count = 0
		for test_file in test_files:

			predicted_label = classify(test_file)

			# Print the predicted output
			start_index = test_file.find('/') + 1
			end_index = test_file.rfind('/')
			original_label = test_file[start_index:end_index].split("/")[::-1][0]

			if (original_label) == predicted_label:
				printgreen('Original: ' + original_label + ' / Predicted: ' + predicted_label)
				if original_label=="off":
					correctoff +=1
				else:
					correcton +=1
			else:
				printred('Original: ' + original_label + ' / Predicted: ' + predicted_label)
			count+=1
			print("---------------------------")
		print("On: " + str(correcton) + " / " + str(count/2))
		print("Off: " + str(correctoff) + " / " + str(count/2))
		print("Success: " + str(correcton + correctoff) + " / " + str(count))

def print_features():
	# Read the input audio file
	file = '/home/james/Documents/git/SpeechRecognition/hmm-speech-recognition-0.1/audio/apple/apple01.wav'
	sampling_freq, signal = wavfile.read(file)
	# Take the first 10,000 samples for analysis
	signal = signal[:10000]

	# Extract the MFCC features
	features_mfcc = mfcc(signal, sampling_freq)

	# Print the parameters for MFCC
	print('\nMFCC:\nNumber of windows =', features_mfcc.shape[0])
	print('Length of each feature =', features_mfcc.shape[1])

	# Plot the features
	features_mfcc = features_mfcc.T
	plt.matshow(features_mfcc)
	plt.title('MFCC')

	# Extract the Filter Bank features
	features_fb = logfbank(signal, sampling_freq)
	# Print the parameters for Filter Bank
	print('\nFilter bank:\nNumber of windows =', features_fb.shape[0])
	print('Length of each feature =', features_fb.shape[1])

	# Plot the features
	features_fb = features_fb.T
	plt.matshow(features_fb)
	plt.title('Filter bank')
	plt.show()

def is_it_on_or_off():
	with warnings.catch_warnings():
		warnings.simplefilter('ignore')
		#datapath = 'hmm-speech-recognition-0.1/audio/'
		datapath = 'data/'
		# Build an HMM model for each word
		word_models = build_models(datapath)
		run_tests(["./temp.wav"], word_models)

		#return word_models

def query_tester(word_models):
	while True:
		print("input filename: ")
		fname = input()
		if "on" in fname:
			fname = "data/on/" + fname + ".wav"
		elif "off" in fname:
			fname = "data/off/" + fname + ".wav"
		run_tests([fname], word_models)

if __name__=='__main__':
	warnings.filterwarnings("ignore")
	with warnings.catch_warnings():
		warnings.simplefilter('ignore')
		#datapath = 'hmm-speech-recognition-0.1/audio/'
		datapath = 'data/'
		# Build an HMM model for each word
		word_models = build_models(datapath)

		test_files = []
		for root, dirs, files in os.walk(datapath):
			for filename in (x for x in files):
				filepath = os.path.join(root, filename)
				test_files.append(filepath)
		
		run_tests(test_files, word_models)
		#query_tester(word_models)