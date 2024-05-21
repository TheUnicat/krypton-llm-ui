import torch
from TTS.api import TTS

device = 'cpu'

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# Run TTS
# ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
while True:
    text = input("Enter text: ")
# Text to speech to a file
    tts.tts_to_file(text=text, speaker_wav="/Users/hongyang/Downloads/real_tenma.wav", language="en", file_path="/Users/hongyang/Downloads/gabriel.wav")