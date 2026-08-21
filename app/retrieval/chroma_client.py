import logging
import os

import chromadb
from chromadb.config import Settings
from chromadb.errors import InvalidCollectionException
from app.config import settings

logger = logging.getLogger(__name__)


# Singleton pattern for ChromaDB client
class ChromaDBClient:
    _instance = None

    @staticmethod
    def _load_or_create_collection(client):
        """
        Safely load an existing collection or create a fresh one on first run.
        Never calls client.reset() — that destroys all indexed data.
        """
        try:
            # Prefer loading the existing collection to preserve indexed data.
            collection = client.get_collection(name=settings.collection_name)
            doc_count = collection.count()
            logger.info(
                "[RAG] Loaded existing ChromaDB collection '%s' with %d documents.",
                settings.collection_name,
                doc_count,
            )
            if doc_count == 0:
                logger.warning(
                    "[RAG] Collection '%s' is EMPTY. Run the ingestion pipeline "
                    "(`bash scripts/ingest.sh`) to populate it before querying.",
                    settings.collection_name,
                )
            return collection
        except (InvalidCollectionException, ValueError):
            # Collection doesn't exist yet — first-time setup.
            logger.info(
                "[RAG] Collection '%s' not found. Creating new collection.",
                settings.collection_name,
            )
            return client.create_collection(
                name=settings.collection_name,
                metadata={"hnsw:space": "cosine", "hnsw:M": 16, "hnsw:construction_ef": 100},
            )

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaDBClient, cls).__new__(cls)
            os.makedirs(settings.chroma_path, exist_ok=True)
            cls._instance.client = chromadb.PersistentClient(
                path=settings.chroma_path,
                settings=Settings(anonymized_telemetry=False, allow_reset=True),
            )
            cls._instance.collection = cls._load_or_create_collection(cls._instance.client)
        return cls._instance


chroma_db = ChromaDBClient()
