import os
import sys
import shutil
import base64
import requests
import imageio_ffmpeg
import warnings
from deep_translator import GoogleTranslator #alternatively MyMemoryTranslator can be used to remove restriction abt set limit but then the auto needs to be set to a specific language

# setup local ffmpeg
ffmpeg_source = imageio_ffmpeg.get_ffmpeg_exe()
venv_scripts_dir = os.path.join(sys.prefix, "Scripts")
target_ffmpeg = os.path.join(venv_scripts_dir, "ffmpeg.exe")

if not os.path.exists(target_ffmpeg):
    shutil.copyfile(ffmpeg_source, target_ffmpeg)

import whisper

warnings.filterwarnings("ignore", category=UserWarning)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


audio_path = "sample_audio.mpeg"
image_path = "sample.jpg"

if not os.path.exists(audio_path) or not os.path.exists(image_path):
    print("\n[ERROR] Couldn't translate: Required input files  were not found in folder.")
    sys.exit(1)

# audio stream (Whisper)
try:
    whisper_model = whisper.load_model("base")
    transcription_result = whisper_model.transcribe(audio_path)
    spoken_text = transcription_result['text'].strip()
    print(f"Spoken Text (Whisper): \"{spoken_text}\"")
except Exception as e:
    print(f"\n[ERROR] Couldn't process audio: {e}")
    sys.exit(1)

# visual stream (Ollama / LLaVA)
try:
    image_b64 = encode_image(image_path)
    ollama_url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llava",
        "prompt": "Briefly describe the frame",
        "images": [image_b64],
        "stream": False
    }
    response = requests.post(ollama_url, json=payload)
    
    if response.status_code == 200:
        visual_context = response.json()['response'].strip()
        print(f"Visual Context (LLaVA): \"{visual_context}\"")
    else:
        print(f"\n[ERROR] Couldn't translate visual stream: Ollama returned status code {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] Couldn't process image: {e}")
    sys.exit(1)

# FUSION LAYER
fused_prompt = f"Speaker said: '{spoken_text}'. Visual context: {visual_context}"
print(f"Fused Semantic Output: {fused_prompt}")

# translation and localization
print("\n--- 4. Translating Fused Result ---")
try:
    translated_text = GoogleTranslator(source='auto', target='en').translate(fused_prompt)
    print(f"Final Localized Output (English): {translated_text}")
except Exception as e:
    print(f"\n[ERROR] Couldn't translate output: {e}")