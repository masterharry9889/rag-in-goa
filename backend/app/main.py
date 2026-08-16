from fastapi import FastAPI
from app.api.routes_voice import router as voice_router
from app.api.routes_health import router as health_router
from app.api.routes_config import router as config_router
from contextlib import asynccontextmanager
import os
from app.indexing.build_index import build_index
import yaml
import chromadb

VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/chroma_db")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load config to get collection name
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.yaml")
    collection_name = "msmarco_xi_passages"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            collection_name = config.get("retrieval", {}).get("vector_db", {}).get("collection_name", collection_name)
    except Exception:
        pass

    # Check if the index exists
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    try:
        client.get_collection(name=collection_name)
        print("Vector index found.")
    except Exception:
        print(f"Vector index not found at {VECTOR_DB_PATH}. Attempting to build...")
        try:
            build_index()  # Process full dataset without limits
            print("Index built successfully.")
        except Exception as e:
            print(f"Failed to build index: {e}")
            raise RuntimeError(f"Failed to build index: {e}") from e
    yield
    # Shutdown event (if any) can go here

app = FastAPI(title="Voice-Enabled RAG System", lifespan=lifespan)
app.include_router(voice_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(config_router, prefix="/api")