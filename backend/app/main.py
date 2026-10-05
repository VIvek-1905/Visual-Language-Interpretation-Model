from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import upload

app = FastAPI(title="Multimodal API v2")

# allow react frontend ki setting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)

@app.get("/")
async def root():
    return {"status": "online", "msg": "API Gateway running rn"}