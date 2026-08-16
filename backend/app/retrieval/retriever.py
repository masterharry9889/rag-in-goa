from typing import List, Dict, Any
from app.indexing.chroma_store import ChromaStore
from app.indexing.embedder import Embedder

class Retriever:
    def __init__(self, vector_store: ChromaStore, embedder: Embedder, k: int = 5):
        self.vector_store = vector_store
        self.embedder = embedder
        self.k = k

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve top-k relevant chunks for the query."""
        query_embedding = self.embedder.embed_query(query)
        return self.vector_store.similarity_search(query_embedding, k=self.k)