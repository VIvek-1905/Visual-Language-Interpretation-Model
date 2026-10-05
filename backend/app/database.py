import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load variables from .env file
load_dotenv()

MONGO_DETAILS = os.getenv("MONGO_DETAILS")

if not MONGO_DETAILS:
    raise ValueError("MONGO_DETAILS key missing in .env file")

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.multimodal_translation

# This is the exact variable Python is looking for
results_collection = database.get_collection("translation_results")