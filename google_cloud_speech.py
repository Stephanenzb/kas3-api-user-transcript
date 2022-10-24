from google.cloud import speech
import os 
import io 

#test file 

client = speech.SpeechClient()
gcs_uri = "gs://kas-audio/"


audio = speech.RecognitionAudio(uri=gcs_uri)

config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
    sample_rate_hertz=48000,
    language_code="en-US",
    audio_channel_count = 2
)

# Detects speech in the audio file
response = client.recognize(config=config, audio=audio)

for result in response.results:
    print("Transcript: {}".format(result.alternatives[0].transcript))
