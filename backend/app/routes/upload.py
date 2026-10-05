import os
import asyncio
import tempfile
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from backend.app.database import results_collection
from ai_engine.audio_processor import AudioProcessor
from ai_engine.vision_processor import VisionProcessor
from ai_engine.fusion_pipeline import SemanticFusionEngine

router = APIRouter()

# init ai classes 1x only btw
audio_processor = AudioProcessor()
vision_processor = VisionProcessor()
fusion_engine = SemanticFusionEngine()

@router.post(
    "/api/translate-video", 
    tags=["Core AI Pipeline"],
    summary="Run Multimodal Arbitration"
)
async def translate_video(file: UploadFile = File(...)):
    try:
        # temp file for upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(await file.read())
            temp_video_path = temp_video.name
    except Exception as e:
        raise HTTPException(status_code=500, detail="file ingestion failed")

    try:
        # dummy frame rn tbvh, will make dynamic later
        dummy_frame_path = os.path.join("test_lab", "sample.jpeg")
        if not os.path.exists(dummy_frame_path):
            raise HTTPException(status_code=500, detail="missing keyframe")

        # run both async so it doesn't block u
        audio_task = asyncio.create_task(audio_processor.transcribe(temp_video_path))
        visual_task = asyncio.create_task(vision_processor.analyze_frame(dummy_frame_path))
        
        spoken_text, visual_context = await asyncio.gather(audio_task, visual_task)

        # fuse & translate
        fused_prompt = fusion_engine.fuse_contexts(spoken_text, visual_context)
        translated_text = fusion_engine.translate_fused_context(fused_prompt)

        # save to mongo
        db_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "spoken_text": spoken_text,
            "visual_context": visual_context,
            "fused_prompt": fused_prompt,
            "translation": translated_text
        }
        await results_collection.insert_one(db_record)

        # cleanup
        os.remove(temp_video_path)

        return JSONResponse(content=db_record)

    except Exception as e:
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        raise HTTPException(status_code=500, detail=str(e))