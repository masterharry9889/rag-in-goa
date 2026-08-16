import faiss
import numpy as np
import sqlite3
import json
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
        
        if hasattr(self, '_db_path') and self._db_path:
            # Fetch from SQLite database
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            for i, idx in enumerate(indices[0]):
                if idx >= 0:
                    cursor.execute('SELECT text, metadata FROM chunks WHERE id = ?', (int(idx),))
                    row = cursor.fetchone()
                    if row:
                        results.append({
                            "text": row[0],
                            "metadata": json.loads(row[1]) if row[1] else {},
                            "distance": float(distances[0][i])
                        })
            conn.close()
        else:
            # Fallback to in-memory list (if not yet persisted)
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(self.texts):  # safety check
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
        
        # Save texts and metadatas into an SQLite database
        db_path = f"{path}_texts.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS chunks
                          (id INTEGER PRIMARY KEY, text TEXT, metadata TEXT)''')
        
        # Clear existing data just in case
        cursor.execute('DELETE FROM chunks')
        
        # Insert all
        for i, (text, meta) in enumerate(zip(self.texts, self.metadatas)):
            cursor.execute('INSERT INTO chunks (id, text, metadata) VALUES (?, ?, ?)',
                           (i, text, json.dumps(meta)))
        
        conn.commit()
        conn.close()
        self._db_path = db_path

    def load(self, path: str):
        """Load the vector store from disk."""
        # Load the index
        self.index = faiss.read_index(f"{path}.index")
        
        # Keep track of DB path for retrieval
        self._db_path = f"{path}_texts.db"
        
        # Clear in-memory lists since we will fetch from DB directly
        self.texts = []
        self.metadatas = []