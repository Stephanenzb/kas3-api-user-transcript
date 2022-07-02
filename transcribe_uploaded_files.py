from google.cloud import speech
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file('./credentials/credentials.json')


def transcribe_from_gcs(gcs_uri):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    output = ""

    client = speech.SpeechClient(
        credentials= credentials
    )

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
        audio_channel_count = 1
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=900)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        print(result)
        # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(result.alternatives[0].transcript))
        output += result.alternatives[0].transcript + '\n'
        print("Confidence: {}".format(result.alternatives[0].confidence))
    return output
