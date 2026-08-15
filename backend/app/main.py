from fastapi import FastAPI
from api.routes_voice import router as voice_router
from api.routes_health import router as health_router

app = FastAPI(title="Voice-Enabled RAG System")
app.include_router(voice_router, prefix="/api")
app.include_router(health_router, prefix="/api")