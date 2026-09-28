import os
import base64
import asyncio
import requests
from config import OLLAMA_API_URL, VISION_MODEL_NAME

class VisionProcessor:
    '''
    Handles paralle image encoding and visual context extraction 
    using LLaVA via Ollama.
    '''
    def __init__(self):
        self.api_url = OLLAMA_API_URL
        self.model_name = VISION_MODEL_NAME

    def _encode_image(self, image_path: str) -> str:
        '''Securely verifies and encodes image '''
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"[VISION ERROR] Keyframe not found at {image_path}")
        
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    async def analyze_frame(self, image_path: str, prompt: str = "Describe the object or scene visible in this frame in one short, precise sentence.") -> str:
        '''
        parallely sends a frame to the local Vision-Language Model 
        without blocking the main server thread.
        '''
        try:
            image_b64 = self._encode_image(image_path)
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "images": [image_b64],
                "stream": False
            }
            
            # Offload the linear HTTP request to a background thread
            print(f"[VISION] Analyzing frame using {self.model_name}...")
            response = await asyncio.to_thread(requests.post, self.api_url, json=payload)
            response.raise_for_status()  # Automatically catch errors
            
            return response.json().get('response', '').strip()
            
        except requests.exceptions.RequestException as e:
            print(f"[VISION ERROR] Local LLaVA API connection failed: {e}")
            raise RuntimeError("Vision API connection failed. Is Ollama running?") from e
        except Exception as e:
            print(f"[VISION ERROR] Frame analysis failed: {e}")
            raise RuntimeError("Visual context extraction failed") from e