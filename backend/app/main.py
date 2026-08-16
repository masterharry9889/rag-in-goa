from fastapi import FastAPI
from app.api.routes_voice import router as voice_router
from app.api.routes_health import router as health_router
from app.api.routes_config import router as config_router
from contextlib import asynccontextmanager
import os
from app.indexing.build_index import build_index

VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/processed/vector_db")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Check if the index exists
    index_file = f"{VECTOR_DB_PATH}.index"
    texts_file = f"{VECTOR_DB_PATH}_texts.db"
    if not (os.path.exists(index_file) and os.path.exists(texts_file)):
        print(f"Vector index not found at {VECTOR_DB_PATH}. Attempting to build...")
        try:
            build_index()  # Process full dataset without limits
            print("Index built successfully.")
        except Exception as e:
            print(f"Failed to build index: {e}")
            raise RuntimeError(f"Failed to build index: {e}") from e
    else:
        print("Vector index found.")
    yield
    # Shutdown event (if any) can go here

app = FastAPI(title="Voice-Enabled RAG System", lifespan=lifespan)
app.include_router(voice_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(config_router, prefix="/api")