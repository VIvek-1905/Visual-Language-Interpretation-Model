import os
import sys
import shutil
import asyncio
import warnings
import whisper
import imageio_ffmpeg
from ai_engine.config import WHISPER_MODEL_SIZE

warnings.filterwarnings("ignore", category=UserWarning)

class AudioProcessor:
    def __init__(self):
        self.model = None
        self._ensure_ffmpeg_path()

    def _ensure_ffmpeg_path(self):
        ffmpeg_source = imageio_ffmpeg.get_ffmpeg_exe()
        venv_scripts_dir = os.path.join(sys.prefix, "Scripts")
        target_ffmpeg = os.path.join(venv_scripts_dir, "ffmpeg.exe")

        if not os.path.exists(target_ffmpeg):
            shutil.copyfile(ffmpeg_source, target_ffmpeg)
            print(f"[AUDIO] FFmpeg binary mapped to {target_ffmpeg}")

    def load_model(self):
        if self.model is None:
            print(f"[AUDIO] Loading Whisper '{WHISPER_MODEL_SIZE}' model into memory")
            self.model = whisper.load_model(WHISPER_MODEL_SIZE)

    async def transcribe(self, file_path: str) -> dict:
        self.load_model() 
        try:
            result = await asyncio.to_thread(self.model.transcribe, file_path)
            # Whisper natively auto-detects the language dawg!
            return {
                "text": result['text'].strip(),
                "detected_language": result.get('language', 'unknown')
            }
        except Exception as e:
            print(f"[AUDIO ERROR] Transcription failed: {e}")
            raise RuntimeError("Audio transcription failed") from e