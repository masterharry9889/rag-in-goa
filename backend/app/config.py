import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # STT Configuration
    STT_PROVIDER: str = "sarvam"  # or "elevenlabs"
    SARVAM_API_KEY: str
    ELEVENLABS_API_KEY: str
    
    # LLM Configuration
    LLM_PROVIDER: str = "openai"  # or "anthropic", "groq", etc.
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    GROQ_API_KEY: str
    
    # Vector Database
    VECTOR_DB_PATH: str = "./data/processed/vector_db"
    
    # Latency Budget Constants (in milliseconds)
    LATENCY_BUDGET_STT: int = 50
    LATENCY_BUDGET_CHUNKING: int = 30
    LATENCY_BUDGET_RETRIEVAL: int = 70
    LATENCY_BUDGET_GENERATION: int = 40
    LATENCY_BUDGET_GUARDRAILS: int = 10
    
    # Chunking Configuration
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    
    # Retrieval Configuration
    TOP_K: int = 5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()