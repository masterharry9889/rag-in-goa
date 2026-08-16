import chromadb
from typing import List, Dict, Any
import uuid

class ChromaStore:
    def __init__(self, persist_directory: str, collection_name: str = "passages"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_texts(self, texts: List[str], embeddings: List[List[float]], metadatas: List[Dict] = None) -> List[str]:
        """Add texts to the Chroma vector store."""
        if metadatas is None:
            metadatas = [{}] * len(texts)
            
        # Ensure metadata values are str, int, float or bool (ChromaDB requirement)
        safe_metadatas = []
        for meta in metadatas:
            safe_meta = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    safe_meta[k] = v
                else:
                    safe_meta[k] = str(v)
            safe_metadatas.append(safe_meta)
            
        ids = [str(uuid.uuid4()) for _ in texts]
        
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=safe_metadatas,
            ids=ids
        )
        return ids

    def persist(self, path: str = None):
        """Chroma PersistentClient automatically persists."""
        pass
