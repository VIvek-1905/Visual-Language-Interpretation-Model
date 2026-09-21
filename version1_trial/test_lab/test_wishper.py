import os
import sys
import shutil
import imageio_ffmpeg
import warnings

ffmpeg_source = imageio_ffmpeg.get_ffmpeg_exe()
venv_scripts_dir = os.path.join(sys.prefix, "Scripts")
target_ffmpeg = os.path.join(venv_scripts_dir, "ffmpeg.exe")

if not os.path.exists(target_ffmpeg):
    print("Setting up local ffmpeg.exe inside venv...")
    shutil.copyfile(ffmpeg_source, target_ffmpeg)

import whisper

# Suppress basic warnings
warnings.filterwarnings("ignore", category=UserWarning)

print("Loading Whisper 'base' model...")
model = whisper.load_model("base")

media_path = "sample_audio.mpeg" 

if not os.path.exists(media_path):
    print(f"\n[ERROR] Could not find '{media_path}' in test_lab!")
    print("Please place an audio/video file in test_lab and update the media_path variable.")
else:
    print(f"Transcribing {media_path}... wait a moment.")
    result = model.transcribe(media_path)
    print("\nWhisper transcribed:")
    print(f"\"{result['text'].strip()}\"")