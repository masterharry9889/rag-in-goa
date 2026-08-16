"""
Offline script to build the vector index from a dataset.
Steps:
1. Load dataset (e.g., from Hugging Face or local files)
2. Filter selected passages and global deduplicate
3. Chunk the documents using a selected chunking strategy
4. Embed the chunks
5. Add to vector store and persist
"""

import os
import json
import yaml
import hashlib
from typing import List, Dict, Any, Optional

def build_index():
    # Load config
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    config_path = os.path.join(base_dir, "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    chunking_strategy = config["chunking"]["default_strategy"]
    embed_model = config["retrieval"]["embedding_model"]
    persist_dir = config["retrieval"]["vector_db"]["persist_directory"]
    collection_name = config["retrieval"]["vector_db"]["collection_name"]
    
    # Initialize chunker
    from app.chunking.registry import ChunkerRegistry
    if chunking_strategy == "metadata_aware":
        align = config["chunking"]["metadata_aware"]["align_to_passage"]
        from app.chunking.metadata_aware import MetadataAwareChunker
        chunker = MetadataAwareChunker(align_to_passage=align)
    else:
        chunk_size = config["chunking"]["fixed_size"]["chunk_size_tokens"]
        overlap_pct = config["chunking"]["fixed_size"]["overlap_pct"]
        chunk_overlap = int(chunk_size * overlap_pct)
        chunker = ChunkerRegistry.get_strategy(chunking_strategy, chunk_size=chunk_size, overlap=chunk_overlap)
        
    from app.indexing.embedder import Embedder
    embedder = Embedder(model_name=embed_model)
    
    from app.indexing.chroma_store import ChromaStore
    persist_path = os.path.join(base_dir, persist_dir)
    vector_store = ChromaStore(persist_directory=persist_path, collection_name=collection_name)
    
    import pyarrow.parquet as pq
    
    selected_only = config.get("indexing", {}).get("selected_passages_only", True)
    local_file = os.path.join(base_dir, "data", "raw", "hintrain.parquet")
    print(f"Loading local dataset from {local_file}...", flush=True)
    if not os.path.exists(local_file):
        raise FileNotFoundError(f"Local dataset file not found at {local_file}")
        
    print("Reading parquet file to extract and deduplicate passages...", flush=True)
    parquet_file = pq.ParquetFile(local_file)

    total_filtered = 0
    unique_passages = {} # passage_hash -> {"text": str, "query_ids": set()}
    
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
                
                passage_hash = hashlib.sha256(passage_text.encode('utf-8')).hexdigest()
                if passage_hash in unique_passages:
                    unique_passages[passage_hash]["query_ids"].add(query_id)
                else:
                    unique_passages[passage_hash] = {
                        "text": passage_text,
                        "query_ids": {query_id}
                    }

    print(f"Total passages filtered out (is_selected=0): {total_filtered}", flush=True)
    print(f"Total unique canonical passages to index: {len(unique_passages)}", flush=True)
    
    print("Chunking and Embedding...", flush=True)
    batch_size = 128
    batch_chunks = []
    batch_metadatas = []
    total_embedded = 0

    for passage_hash, data in unique_passages.items():
        passage_text = data["text"]
        query_ids_str = ",".join(sorted(data["query_ids"]))
        
        chunks = chunker.chunk(passage_text, metadata={"query_ids": query_ids_str, "passage_hash": passage_hash})
        batch_chunks.extend(chunks)
        
        meta = {"query_ids": query_ids_str, "passage_hash": passage_hash}
        batch_metadatas.extend([meta] * len(chunks))
        
        if len(batch_chunks) >= batch_size:
            print(f"Embedding batch of {len(batch_chunks)} chunks... Total embedded: {total_embedded}", flush=True)
            embeddings = embedder.embed(batch_chunks)
            vector_store.add_texts(batch_chunks, embeddings=embeddings, metadatas=batch_metadatas)
            total_embedded += len(batch_chunks)
            batch_chunks = []
            batch_metadatas = []

    # Process remaining chunks
    if batch_chunks:
        print(f"Embedding final batch of {len(batch_chunks)} chunks...", flush=True)
        embeddings = embedder.embed(batch_chunks)
        vector_store.add_texts(batch_chunks, embeddings=embeddings, metadatas=batch_metadatas)
        total_embedded += len(batch_chunks)

    print(f"Total chunks embedded globally: {total_embedded}", flush=True)
    
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
    print(f"Final data/chroma_db size: {db_size_mb:.2f} MB", flush=True)
    print("Index built successfully!", flush=True)

if __name__ == "__main__":
    build_index()