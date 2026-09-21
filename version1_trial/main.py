from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv
import sys
import shutil
import base64
import asyncio
import tempfile
import requests
import imageio_ffmpeg
import warnings
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from deep_translator import GoogleTranslator
import whisper

#System Setup for Whisper
ffmpeg_source = imageio_ffmpeg.get_ffmpeg_exe()
venv_scripts_dir = os.path.join(sys.prefix, "Scripts")
target_ffmpeg = os.path.join(venv_scripts_dir, "ffmpeg.exe")

if not os.path.exists(target_ffmpeg):
    shutil.copyfile(ffmpeg_source, target_ffmpeg)

warnings.filterwarnings("ignore", category=UserWarning)

# Pre-load Whisper model
print("Loading Whisper model...")
whisper_model = whisper.load_model("base")


app = FastAPI(
    title="Multimodal Translation API",
    description="Asynchronous backend for context-aware multimodal translation",
    version="1.0.0"
)

#db setup
load_dotenv()
mongo_details=os.getenv("mongo_details")
client=AsyncIOMotorClient(mongo_details)
database=client.multimodal_translationn
results_collection=database.get_collection("translation_results")


#Helper Functions
def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def process_audio(file_path: str) -> str:
    """Extracts text from the audio track using Whisper."""
    try:
        # Running Whisper in a separate thread so it doesn't block the async server
        result = await asyncio.to_thread(whisper_model.transcribe, file_path)
        return result['text'].strip()
    except Exception as e:
        print(f"Audio processing error: {e}")
        return "Error transcribing audio."

async def process_visual(image_path: str) -> str:
    """Analyzes a frame using local Ollama (LLaVA)."""
    try:
        image_b64 = encode_image(image_path)
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llava",
            "prompt": "Briefly describe what object, chart, or scene is visible in this frame in one short sentence.",
            "images": [image_b64],
            "stream": False
        }
        # Run the requests call in a separate thread to keep API responsive
        response = await asyncio.to_thread(requests.post, url, json=payload)
        
        if response.status_code == 200:
            return response.json()['response'].strip()
        else:
            return f"Error: Ollama returned status {response.status_code}"
    except Exception as e:
        print(f"Visual processing error: {e}")
        return "Error analyzing visual context."

# --- Core API Endpoints ---
@app.get("/")
async def root():
    return {"status": "online", "message": "Gateway is running"}

@app.post("/api/translate-video")
async def translate_video(file: UploadFile = File(...)):
    """Accepts a video, processes audio and visual context concurrently, and returns a translation."""
    
    # Save the uploaded file to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            content = await file.read()
            temp_video.write(content)
            temp_video_path = temp_video.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {e}")

    try:
        dummy_frame_path = os.path.join("test_lab", "sample.jpeg")
        
        if not os.path.exists(dummy_frame_path):
            raise HTTPException(status_code=500, detail="Missing test keyframe (sample.jpeg) in test_lab folder.")

        audio_task = asyncio.create_task(process_audio(temp_video_path))
        visual_task = asyncio.create_task(process_visual(dummy_frame_path))
        
        spoken_text, visual_context = await asyncio.gather(audio_task, visual_task)

        # Multimodal Fusion
        fused_prompt = f"Speaker said: '{spoken_text}'. Visual context: {visual_context}"
        
        # Translation
        translated_text = GoogleTranslator(source='auto', target='en').translate(fused_prompt)

        # Cleanup temp file
        os.remove(temp_video_path)

        # Database Persistence
        db_record = {
            "timestamp": datetime.now(datetime.UTC).isoformat(),
            "spoken_text": spoken_text,
            "visual_context": visual_context,
            "fused_prompt": fused_prompt,
            "translation": translated_text
        }
        await results_collection.insert_one(db_record)

        return JSONResponse(content={
            "audio_transcription": spoken_text,
            "visual_context": visual_context,
            "fused_prompt": fused_prompt,
            "translation": translated_text
        })

    except Exception as e:
        #ensure temp file deleted
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        raise HTTPException(status_code=500, detail=str(e))