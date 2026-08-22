import logging
import os

import chromadb
from chromadb.config import Settings
from app.config import settings

logger = logging.getLogger(__name__)


# Singleton pattern for ChromaDB client
class ChromaDBClient:
    _instance = None

    @staticmethod
    def _load_or_create_collection(client):
        """
        Load an existing collection when possible, otherwise create one.

        ChromaDB 1.x dropped the older InvalidCollectionException symbol, and
        corrupt collection metadata can surface as a KeyError during collection
        lookup. In that case, reset the underlying storage and retry once so the
        RAG index can be rebuilt instead of failing forever.
        """
        collection_config = {
            "hnsw:space": "cosine",
            "hnsw:M": 16,
            "hnsw:construction_ef": 100,
        }

        get_collection = getattr(client, "get_collection", None)
        if callable(get_collection):
            try:
                collection = get_collection(name=settings.collection_name)
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
            except Exception as exc:
                # Missing collection or stale metadata can trigger ValueError /
                # KeyError / NotFoundError / InvalidCollectionException depending
                # on the ChromaDB version.
                _allowed = (KeyError, ValueError, TypeError)
                for _exc_name in ("NotFoundError", "InvalidCollectionException"):
                    try:
                        _exc_cls = getattr(
                            __import__("chromadb.errors", fromlist=[_exc_name]),
                            _exc_name,
                        )
                        _allowed = (*_allowed, _exc_cls)
                    except (ImportError, AttributeError):
                        pass
                if not isinstance(exc, _allowed):
                    # Re-raise unexpected errors so we don't silently hide real faults.
                    raise

        try:
            logger.info(
                "[RAG] Collection '%s' not found. Creating new collection.",
                settings.collection_name,
            )
            return client.get_or_create_collection(
                name=settings.collection_name,
                metadata=collection_config,
            )
        except KeyError as exc:
            if "_type" not in str(exc):
                raise
            logger.warning(
                "[RAG] Collection metadata is corrupt for '%s'; resetting ChromaDB "
                "storage and recreating the collection.",
                settings.collection_name,
            )
            client.reset()
            return client.get_or_create_collection(
                name=settings.collection_name,
                metadata=collection_config,
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
