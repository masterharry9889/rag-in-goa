from app.retrieval.chroma_client import chroma_db
from app.retrieval.embedder import embedder
from typing import List, Dict, Any

class HybridRetriever:
    def __init__(self, top_k: int = 3):
        self.collection = chroma_db.collection
        self.top_k = top_k

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        # Generate query embedding
        query_embedding = embedder.embed_texts([query])[0]
        
        # Dense retrieval from ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        chunks = []
        if results and results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                # Check distance to avoid very poor matches
                if results["distances"][0][i] > 0.8: # high cosine distance
                    continue
                    
                chunks.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": 1.0 - results["distances"][0][i] # roughly convert to similarity
                })
                
        # Optional: BM25 fusion could go here, but since ChromaDB doesn't do native BM25 
        # and we need to stay within 200ms latency budget, we stick to pure dense for now.
        # Alternatively, a lightweight BM25 layer could be added in-memory.
        
        return chunks
