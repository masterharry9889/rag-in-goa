import chromadb
from chromadb.config import Settings
from app.config import settings

# Singleton pattern for ChromaDB client
class ChromaDBClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaDBClient, cls).__new__(cls)
            cls._instance.client = chromadb.PersistentClient(
                path=settings.chroma_path,
                settings=Settings(anonymized_telemetry=False, allow_reset=False)
            )
            # Collection metadata includes settings for compact storage and faster recall
            cls._instance.collection = cls._instance.client.get_or_create_collection(
                name=settings.collection_name,
                metadata={"hnsw:space": "cosine", "hnsw:M": 16, "hnsw:construction_ef": 100}
            )
        return cls._instance

chroma_db = ChromaDBClient()
