from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    sarvam_api_key: str = "SARVAM_API_KEY"
    groq_api_key: str = "GROQ_API_KEY"
    
    # LLM Settings
    groq_model: str = "llama3-8b-8192"

    # ChromaDB settings
    chroma_path: str = "data/chroma"
    collection_name: str = "hinval_msmarco"

    # Embedding model settings (using a compact model for Hindi)
    embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dimension: int = 384

    # Chunking settings
    max_indexed_passages: int = 5000  # Limit for indexing to keep DB small

    # Latency settings
    retrieval_latency_target_ms: int = 200

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()