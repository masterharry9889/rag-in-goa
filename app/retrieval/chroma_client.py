import os

import chromadb
from chromadb.config import Settings
from app.config import settings


# Singleton pattern for ChromaDB client
class ChromaDBClient:
    _instance = None

    @staticmethod
    def _create_collection(client):
        metadata = {"hnsw:space": "cosine", "hnsw:M": 16, "hnsw:construction_ef": 100}
        try:
            return client.get_or_create_collection(
                name=settings.collection_name,
                metadata=metadata,
            )
        except (KeyError, ValueError, TypeError) as exc:
            if "_type" not in str(exc) and "from_json" not in str(exc):
                raise

            os.makedirs(settings.chroma_path, exist_ok=True)
            client.reset()
            return client.get_or_create_collection(
                name=settings.collection_name,
                metadata=metadata,
            )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaDBClient, cls).__new__(cls)
            os.makedirs(settings.chroma_path, exist_ok=True)
            cls._instance.client = chromadb.PersistentClient(
                path=settings.chroma_path,
                settings=Settings(anonymized_telemetry=False, allow_reset=True),
            )
            # Collection metadata includes settings for compact storage and faster recall.
            # If the local SQLite state is stale or corrupted from a previous Chroma version,
            # we reset it once and recreate the collection.
            cls._instance.collection = cls._create_collection(cls._instance.client)
        return cls._instance


chroma_db = ChromaDBClient()
