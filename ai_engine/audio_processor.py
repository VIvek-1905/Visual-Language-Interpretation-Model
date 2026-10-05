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
    '''
    Handles parallel audio extraction and transcription using  Whisper.
    Structured as a single class to prevent redundant model loading in memory.
    '''
    def __init__(self):
        self.model = None
        self._ensure_ffmpeg_path()

    def _ensure_ffmpeg_path(self):
        '''Dynamically routes FFmpeg to bypass Windows subprocess restrictions.'''
        ffmpeg_source = imageio_ffmpeg.get_ffmpeg_exe()
        venv_scripts_dir = os.path.join(sys.prefix, "Scripts")
        target_ffmpeg = os.path.join(venv_scripts_dir, "ffmpeg.exe")

        if not os.path.exists(target_ffmpeg):
            shutil.copyfile(ffmpeg_source, target_ffmpeg)
            print(f"[AUDIO] FFmpeg binary mapped to {target_ffmpeg}")

    def load_model(self):
        '''Loads the Whisper model into memory only when first requested.'''
        if self.model is None:
            print(f"[AUDIO] Loading Whisper '{WHISPER_MODEL_SIZE}' model into memory")
            self.model = whisper.load_model(WHISPER_MODEL_SIZE)

    async def transcribe(self, file_path: str) -> str:
        """
        parallely transcribes audio without blocking the main event loop.
        """
        self.load_model() # Ensures model is loaded before transcribing
        
        try:
            # asyncio.to_thread forces this heavy CPU task into the background
            result = await asyncio.to_thread(self.model.transcribe, file_path)
            return result['text'].strip()
        except Exception as e:
            print(f"[AUDIO ERROR] Transcription failed: {e}")
            raise RuntimeError("Audio transcription failed") from e