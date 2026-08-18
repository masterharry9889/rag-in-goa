from app.retrieval.chroma_client import chroma_db
from app.config import settings
import numpy as np

def prune_index(threshold: float = 0.97):
    """
    Post-ingestion pass to drop near-duplicate chunks.
    Scans the collection and removes items that are too similar to each other.
    """
    collection = chroma_db.collection
    print("Fetching all items for pruning...")
    
    # We load in batches if it's too large, but for 5000 passages it should fit in memory
    all_data = collection.get(include=["embeddings"])
    
    if not all_data or not all_data["ids"]:
        print("Empty collection, nothing to prune.")
        return
        
    ids = all_data["ids"]
    embeddings = np.array(all_data["embeddings"])
    
    print(f"Loaded {len(ids)} chunks. Finding near-duplicates (sim > {threshold})...")
    
    to_delete = set()
    
    # A naive O(N^2) comparison for deduplication. 
    # For a real large-scale deployment we would use HNSW graph or LSH.
    # Since max_indexed_passages=5000, N is small enough for this script to run reasonably fast.
    n = len(ids)
    
    # Normalize for cosine similarity dot products
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized_embs = embeddings / (norms + 1e-10)
    
    for i in range(n):
        if ids[i] in to_delete:
            continue
            
        # Compute similarities with remaining vectors
        # Just check the ones after `i`
        if i + 1 < n:
            sims = np.dot(normalized_embs[i+1:], normalized_embs[i])
            # Find indices where sim > threshold
            dup_indices = np.where(sims > threshold)[0]
            
            for dup_idx in dup_indices:
                actual_idx = i + 1 + dup_idx
                to_delete.add(ids[actual_idx])
                
    if to_delete:
        print(f"Found {len(to_delete)} near-duplicates. Removing...")
        collection.delete(ids=list(to_delete))
        print("Pruning complete.")
    else:
        print("No near-duplicates found.")

if __name__ == "__main__":
    prune_index()
