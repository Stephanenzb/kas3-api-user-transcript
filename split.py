from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
import IPython
import librosa
import librosa.display
from pydub import AudioSegment
import os
import soundfile
from google.cloud import storage
from urllib.request import urlopen



#test file
def send_object_to_storage(filename, path):
    storage_client = storage.Client.from_service_account_json('./credentials/credentials.json')
    bucket = storage_client.get_bucket("kas-audio")
    blob = bucket.blob(filename)
    blob.upload_from_filename(path)
    

def load_audio(audio_data):
    y, sr = librosa.load(audio_data, duration=120)
    # And compute the spectrogram magnitude and phase
    S_full, phase = librosa.magphase(librosa.stft(y))
    idx = slice(*librosa.time_to_frames([10, 15], sr=sr))
    S_filter = librosa.decompose.nn_filter(S_full,
                                       aggregate=np.median,
                                       metric='cosine',
                                       width=int(librosa.time_to_frames(2, sr=sr)))
    S_filter = np.minimum(S_full, S_filter)
    margin_i, margin_v = 2, 10
    power = 2

    mask_i = librosa.util.softmask(S_filter,
                               margin_i * (S_full - S_filter),
                               power=power)

    mask_v = librosa.util.softmask(S_full - S_filter,
                               margin_v * S_filter,
                               power=power)
    S_foreground = mask_v * S_full
    S_background = mask_i * S_full
    y_foreground = librosa.istft(S_foreground * phase)
    return y_foreground, sr
                

def song_url(url):
    with urlopen(song_url) as response:
        y, sr = librosa.load(response)    
        S_full, phase = librosa.magphase(librosa.stft(y))
        idx = slice(*librosa.time_to_frames([10, 15], sr=sr))
        S_filter = librosa.decompose.nn_filter(S_full,
                                       aggregate=np.median,
                                       metric='cosine',
                                       width=int(librosa.time_to_frames(2, sr=sr)))
        S_filter = np.minimum(S_full, S_filter)
        margin_i, margin_v = 2, 10
        power = 2

        mask_i = librosa.util.softmask(S_filter,
                               margin_i * (S_full - S_filter),
                               power=power)

        mask_v = librosa.util.softmask(S_full - S_filter,
                               margin_v * S_filter,
                               power=power)
        S_foreground = mask_v * S_full
        S_background = mask_i * S_full
        y_foreground = librosa.istft(S_foreground * phase)
        return y_foreground, sr      

           