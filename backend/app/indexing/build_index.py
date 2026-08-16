"""
Offline script to build the vector index from a dataset.
Steps:
1. Load dataset (e.g., from Hugging Face or local files)
2. Chunk the documents using a selected chunking strategy
3. Embed the chunks
4. Add to vector store and persist
"""

import os
import json
import yaml
from typing import List, Dict, Any, Optional
from datasets import load_dataset
from app.chunking.registry import ChunkerRegistry
from app.indexing.embedder import Embedder
from app.indexing.chroma_store import ChromaStore

def build_index():
    # Load config
    # __file__ is backend/app/indexing/build_index.py
    # we need to go up 4 levels to get to rag-in-goa
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    config_path = os.path.join(base_dir, "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    dataset_name = config["dataset"]["hf_repo"]
    split = config["dataset"]["split"]
    
    chunking_strategy = config["chunking"]["default_strategy"]
    
    embed_model = config["retrieval"]["embedding_model"]
    persist_dir = config["retrieval"]["vector_db"]["persist_directory"]
    collection_name = config["retrieval"]["vector_db"]["collection_name"]
    
    # Initialize chunker
    if chunking_strategy == "metadata_aware":
        align = config["chunking"]["metadata_aware"]["align_to_passage"]
        # Since our updated metadata_aware takes align_to_passage, we'll instantiate it directly for simplicity
        from app.chunking.metadata_aware import MetadataAwareChunker
        chunker = MetadataAwareChunker(align_to_passage=align)
    else:
        chunk_size = config["chunking"]["fixed_size"]["chunk_size_tokens"]
        overlap_pct = config["chunking"]["fixed_size"]["overlap_pct"]
        chunk_overlap = int(chunk_size * overlap_pct)
        chunker = ChunkerRegistry.get_strategy(chunking_strategy, chunk_size=chunk_size, overlap=chunk_overlap)
        
    embedder = Embedder(model_name=embed_model)
    
    persist_path = os.path.join(base_dir, persist_dir)
    vector_store = ChromaStore(persist_directory=persist_path, collection_name=collection_name)
    
    # Load dataset from local parquet file instead of downloading
    import pyarrow.parquet as pq
    import hashlib
    
    selected_only = config.get("indexing", {}).get("selected_passages_only", True)
    
    local_file = os.path.join(base_dir, "data", "raw", "hintrain.parquet")
    print(f"Loading local dataset from {local_file}...")
    if not os.path.exists(local_file):
        raise FileNotFoundError(f"Local dataset file not found at {local_file}")
        
    print("Reading parquet file in batches...")
    parquet_file = pq.ParquetFile(local_file)

    batch_size = 128  # Tuned for throughput
    batch_chunks = []
    batch_metadatas = []
    total_embedded = 0
    total_skipped = 0
    total_filtered = 0
    
    seen_hashes = set()

    for batch_idx, batch in enumerate(parquet_file.iter_batches()):
        for item in batch.to_pylist():
            passages_dict = item.get('passages', {})
            translated_passages = passages_dict.get('Translated_passages', [])
            is_selected = passages_dict.get('is_selected', [])
            query_id = str(item.get('query_id', ''))
            
            if not translated_passages:
                continue
                
            for idx_p, passage in enumerate(translated_passages):
                # Filter by is_selected
                if selected_only and idx_p < len(is_selected) and is_selected[idx_p] != 1:
                    total_filtered += 1
                    continue
                
                passage_text = passage.strip()
                if not passage_text:
                    continue
                
                # Deduplication
                passage_hash = hashlib.sha256(passage_text.encode('utf-8')).hexdigest()
                if passage_hash in seen_hashes:
                    total_skipped += 1
                    continue
                seen_hashes.add(passage_hash)
                
                # Chunk passage
                chunks = chunker.chunk(passage_text, metadata={"query_id": query_id, "passage_hash": passage_hash})
                batch_chunks.extend(chunks)
                
                meta = {"query_id": query_id, "passage_hash": passage_hash}
                batch_metadatas.extend([meta] * len(chunks))
                
                if len(batch_chunks) >= batch_size:
                    print(f"Embedding batch of {len(batch_chunks)} chunks... Total embedded: {total_embedded}")
                    embeddings = embedder.embed(batch_chunks)
                    vector_store.add_texts(batch_chunks, embeddings=embeddings, metadatas=batch_metadatas)
                    total_embedded += len(batch_chunks)
                    batch_chunks = []
                    batch_metadatas = []

    # Process remaining chunks
    if batch_chunks:
        print(f"Embedding final batch of {len(batch_chunks)} chunks...")
        embeddings = embedder.embed(batch_chunks)
        vector_store.add_texts(batch_chunks, embeddings=embeddings, metadatas=batch_metadatas)
        total_embedded += len(batch_chunks)

    print(f"Total chunks embedded: {total_embedded}")
    print(f"Total chunks skipped as duplicates: {total_skipped}")
    print(f"Total chunks filtered by is_selected: {total_filtered}")
    
    # Get directory size
    def get_dir_size(path='.'):
        total = 0
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        total += get_dir_size(entry.path)
        except Exception:
            pass
        return total
        
    db_size_mb = get_dir_size(persist_path) / (1024 * 1024)
    print(f"Final data/chroma_db size: {db_size_mb:.2f} MB")
    
    print("Persisting...")
    vector_store.persist()
    print("Index built successfully!")

if __name__ == "__main__":
    build_index()