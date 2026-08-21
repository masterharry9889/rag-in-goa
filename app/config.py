import os
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

workspace_root = Path(__file__).resolve().parents[1]
cache_dir = workspace_root / ".cache" / "huggingface"
cache_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("HF_HOME", str(cache_dir))
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(cache_dir / "hub"))
os.environ.setdefault("TRANSFORMERS_CACHE", str(cache_dir / "hub"))

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)

    # API Keys
    sarvam_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("SARVAM_API_KEY", "sarvam_api_key"),
    )
    groq_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GROQ_API_KEY", "groq_api_key"),
    )

    # LLM Settings
    # Prefer a model with broad Groq availability and keep a fallback list for
    # model deprecations / 404s from the Groq API.
    groq_model: str = "llama-3.1-8b-instant"
    groq_model_fallbacks: list[str] = [
        "llama-3.3-70b-versatile",
        "llama-3.3-70b-specdec",
        "mixtral-8x7b-32768",
    ]

    # ChromaDB settings
    chroma_path: str = "data/chroma"
    collection_name: str = "hinval_msmarco"

    # Embedding model settings (prefer a multilingual model for Hindi, with a
    # safe fallback for stale/partial HF caches from earlier runs.
    embedding_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_model_fallbacks: list[str] = ["sentence-transformers/all-MiniLM-L6-v2"]
    embedding_dimension: int = 384

    # Chunking settings
    max_indexed_passages: int = 5000  # Limit for indexing to keep DB small

    # Retrieval settings
    retrieval_top_k: int = 5  # Number of chunks to retrieve per query

    # Latency settings
    retrieval_latency_target_ms: int = 200

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    def missing_env_vars(self) -> list[str]:
        missing = []
        if not self.groq_api_key:
            missing.append("GROQ_API_KEY")
        if not self.sarvam_api_key:
            missing.append("SARVAM_API_KEY")
        return missing

settings = Settings()