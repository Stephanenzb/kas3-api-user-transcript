import speech_recognition as sr
from os import path 
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence

def transcribe_audio(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio= r.record(source)
        print( r.recognize_google(audio, language='en-IN', show_all=True))

def transcribe_from_mic():
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

        text = r.recognize_google(audio)
        text = text.lower()

        print(f"Recognized: {text}")

# importing libraries


# a function that splits the audio file into chunks
# and applies speech recognition
def silence_based_conversion(path):

	# open the audio file stored in
	# the local system as a wav file.
	song = AudioSegment.from_wav(path)

	# open a file where we will concatenate
	# and store the recognized text
	fh = open("recognized.txt", "w+")
		
	# split track where silence is 0.5 seconds
	# or more and get chunks
	chunks = split_on_silence(song,
		# must be silent for at least 0.5 seconds
		# or 500 ms. adjust this value based on user
		# requirement. if the speaker stays silent for
		# longer, increase this value. else, decrease it.
		min_silence_len = 500,

		# consider it silent if quieter than -16 dBFS
		# adjust this per requirement
		silence_thresh = -16
	)

	# create a directory to store the audio chunks.
	try:
		os.mkdir('audio_chunks')
	except(FileExistsError):
		pass

	# move into the directory to
	# store the audio files.
	os.chdir('audio_chunks')

	i = 0
	# process each chunk
	for chunk in chunks:
			
		# Create 0.5 seconds silence chunk
		chunk_silent = AudioSegment.silent(duration = 10)

		# add 0.5 sec silence to beginning and
		# end of audio chunk. This is done so that
		# it doesn't seem abruptly sliced.
		audio_chunk = chunk_silent + chunk + chunk_silent

		# export audio chunk and save it in
		# the current directory.
		print("saving chunk{0}.wav".format(i))
		# specify the bitrate to be 192 k
		audio_chunk.export("./chunk{0}.wav".format(i), bitrate ='192k', format ="wav")

		# the name of the newly created chunk
		filename = 'chunk'+str(i)+'.wav'

		print("Processing chunk "+str(i))

		# get the name of the newly created chunk
		# in the AUDIO_FILE variable for later use.
		file = filename

		# create a speech recognition object
		r = sr.Recognizer()

		# recognize the chunk
		with sr.AudioFile(file) as source:
			# remove this if it is not working
			# correctly.
			r.adjust_for_ambient_noise(source)
			audio_listened = r.listen(source)

		try:
			# try converting it to text
			rec = r.recognize_google(audio_listened)
			# write the output to the file.
			fh.write(rec+". ")

		# catch any errors.
		except sr.UnknownValueError:
			print("Could not understand audio")

		except sr.RequestError as e:
			print("Could not request results. check your internet connection")

		i += 1

	os.chdir('..')


#silence_based_conversion("besomebody.wav")
#transcribe_audio("./audio-chunks/chunk21.wav")
#silence_based_conversion("test.wav")
transcribe_from_mic()
