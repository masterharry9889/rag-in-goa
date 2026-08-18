from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_voice, routes_text, routes_health
from app.utils.logging_config import setup_logging
from app.graph.build_graph import build_graph

setup_logging()

app = FastAPI(
    title="Voice-Enabled RAG Backend (rag-in-goa)",
    description="Backend for HH Goa 2026 hackathon Voice RAG system.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Build graph on startup to fail fast if guardrails are missing
@app.on_event("startup")
async def startup_event():
    # Will raise an exception if guardrails are missing
    app.state.graph = build_graph()

app.include_router(routes_health.router, prefix="", tags=["health"])
app.include_router(routes_voice.router, prefix="/voice", tags=["voice"])
app.include_router(routes_text.router, prefix="/text", tags=["text"])
