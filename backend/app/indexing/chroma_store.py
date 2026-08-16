import chromadb
from typing import List, Dict, Any
import uuid

class ChromaStore:
    def __init__(self, persist_directory: str, collection_name: str = "passages", collection_metadata: dict = None):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = collection_name
        
        if collection_metadata is None:
            collection_metadata = {
                "hnsw:space": "cosine",
                "hnsw:construction_ef": 100,
                "hnsw:M": 16
            }
            
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata=collection_metadata
        )

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

    def similarity_search(self, query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve top-k relevant chunks using pre-computed query embedding."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        chunks = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                chunks.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0.0
                })
        return chunks

    def persist(self, path: str = None):
        """Chroma PersistentClient automatically persists."""
        pass
