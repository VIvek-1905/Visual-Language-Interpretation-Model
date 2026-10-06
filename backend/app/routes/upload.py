from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
import uuid
import subprocess
import imageio_ffmpeg

# Your custom imports btw
from backend.app.database import results_collection
from ai_engine.audio_processor import AudioProcessor
from ai_engine.vision_processor import VisionProcessor
from ai_engine.fusion_pipeline import SemanticFusionEngine

router = APIRouter()

audio_processor = AudioProcessor()
vision_processor = VisionProcessor()
fusion_engine = SemanticFusionEngine()

os.makedirs("temp_uploads", exist_ok=True)

@router.post(
    "/api/translate-video", 
    tags=["Core AI Pipeline"],
    summary="Run Multimodal Arbitration"
)
async def translate_video(
    file: UploadFile = File(...),
    # Changed the description to tell frontend devs to use full names tbvh
    target_language: str = Form("Hindi", description="Type full language name (e.g., Hindi, Spanish, Japanese)")
):
    allowed_extensions = ('.mp4', '.mp3', '.avi', '.wav')
    ext = os.path.splitext(file.filename)[1].lower()
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid format tbvh. Upload one of: {allowed_extensions}"
        )
    
    file_id = str(uuid.uuid4())
    temp_file_path = f"temp_uploads/{file_id}{ext}"
    
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 1. Audio processing (now returns a dict with auto-detected language)
        audio_data = await audio_processor.transcribe(temp_file_path)
        spoken_text = audio_data["text"]
        detected_audio_lang = audio_data["detected_language"]
        
        # 2. Vision processing
        visual_context = "No visual context available (audio only file)."
        frame_path = f"temp_uploads/{file_id}.jpg"
        
        if ext in ['.mp4', '.avi']:
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            
            subprocess.run([
                ffmpeg_path, "-y", "-i", temp_file_path, 
                "-ss", "00:00:01", "-vframes", "1", frame_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if os.path.exists(frame_path):
                visual_context = await vision_processor.analyze_frame(frame_path)
                os.remove(frame_path) 
        
        # 3. Arbitrate and translate
        fused_prompt = fusion_engine.fuse_contexts(spoken_text, visual_context)
        final_translation = fusion_engine.translate_fused_context(fused_prompt, target_language)
        
        # 4. Create payload and save to DB
        result_payload = {
            "filename": file.filename,
            "detected_audio_language": detected_audio_lang,
            "target_language": target_language,
            "spoken_text": spoken_text,
            "visual_context": visual_context,
            "fused_prompt": fused_prompt,
            "translation": final_translation,
            "status": "success"
        }
        
        await results_collection.insert_one(result_payload)
        result_payload.pop("_id", None)
        
        return JSONResponse(content=result_payload)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed rn: {str(e)}"
        )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)