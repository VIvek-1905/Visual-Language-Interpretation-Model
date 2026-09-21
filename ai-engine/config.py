import os
'''
AI Engine config module
centralize all model weights, API endpoints and env vars
for decoupled Mul modal ai processing pipelines 
'''

#audio processor settings (allow to switch b/w base and 'Large-v3)
WHISPER_MODEL_SIZE=os.environ.get("WHISPER_MODEL_SIZE", "base")

#visual processor (local endpoint to ensure privacy)
OLLAMA_API_URL=os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
VISION_MODEL_NAME=os.environ.get("VISION_MODEL_NAME", "llava")

#Localization & System Settings
DEFAULT_TARGET_LANGUAGE = os.environ.get("DEFAULT_TARGET_LANGUAGE", "en")

# Ensure secure temporary data directories exist for processing chunks
TEMP_DATA_DIR = os.path.join(os.getcwd(), "data", "samples")
os.makedirs(TEMP_DATA_DIR, exist_ok=True)

print(f"[INIT] AI Engine Configured. Vision Model: {VISION_MODEL_NAME} | Audio Model: {WHISPER_MODEL_SIZE}")

