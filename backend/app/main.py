from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import upload

app = FastAPI(
    title="Multimodal Translation Lab",
    version="Build 2.0",
    description="""
    **experimental visually-grounded translation engine.**
    
    fuses local vision (llava) and audio (whisper) to stop the ai from hallucinating when translating ambiguous audio tbvh.
    """,
    contact={
        "name": "Research Lead", 
        "email": "vivek85tiwari1@gmail.com"
    },
    swagger_ui_parameters={"defaultModelsExpandDepth": -1} # hides messy schemas at the bottom btw
)

# cors config rn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)

# hide this basic route from swagger so it looks clean
@app.get("/", include_in_schema=False)
async def root():
    return {"status": "online", "msg": "API Gateway running rn"}