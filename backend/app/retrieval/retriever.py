from typing import List, Dict, Any
from indexing.vector_store import VectorStoreBase

class Retriever:
    def __init__(self, vector_store: VectorStoreBase, k: int = 5):
        self.vector_store = vector_store
        self.k = k

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve top-k relevant chunks for the query."""
        return self.vector_store.similarity_search(query, k=self.k)