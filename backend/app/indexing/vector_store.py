import faiss
import numpy as np
from typing import List, Dict, Any
from .embedder import Embedder

class VectorStore:
    def __init__(self, embedding_dim: int = 384):  # default for all-MiniLM-L6-v2
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.texts = []
        self.metadatas = []

    def add_texts(self, texts: List[str], metadatas: List[Dict] = None) -> List[str]:
        """Add texts to the vector store."""
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        # We assume an embedder is available; in practice, we would inject it.
        # For now, we'll create one inside the method (not ideal but works for now).
        embedder = Embedder()
        vectors = embedder.embed(texts)
        vectors_np = np.array(vectors).astype('float32')
        
        # Add to FAISS index
        self.index.add(vectors_np)
        
        # Store texts and metadatas
        start_idx = len(self.texts)
        self.texts.extend(texts)
        self.metadatas.extend(metadatas)
        
        # Return IDs (we use the index in the texts list as ID)
        return [str(i) for i in range(start_idx, start_idx + len(texts))]

    def similarity_search(self, query: str, k: int = 4) -> List[Dict]:
        """Search for similar texts."""
        embedder = Embedder()
        query_vector = embedder.embed_query(query)
        query_vector_np = np.array([query_vector]).astype('float32')
        
        # Search the index
        distances, indices = self.index.search(query_vector_np, k)
        
        # Build results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.texts):  # safety check
                results.append({
                    "text": self.texts[idx],
                    "metadata": self.metadatas[idx],
                    "distance": float(distances[0][i])
                })
        return results

    def persist(self, path: str):
        """Persist the vector store to disk."""
        # We'll save the index and the texts/metadatas separately
        faiss.write_index(self.index, f"{path}.index")
        # We can save texts and metadatas as a simple JSON or pickle; for simplicity, we'll use JSON
        import json
        with open(f"{path}_texts.json", "w") as f:
            json.dump({"texts": self.texts, "metadatas": self.metadatas}, f)

    def load(self, path: str):
        """Load the vector store from disk."""
        # Load the index
        self.index = faiss.read_index(f"{path}.index")
        # Load texts and metadatas
        import json
        with open(f"{path}_texts.json", "r") as f:
            data = json.load(f)
            self.texts = data["texts"]
            self.metadatas = data["metadatas"]