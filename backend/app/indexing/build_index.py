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
from typing import List, Dict, Any, Optional
from datasets import load_dataset  # Assuming we use Hugging Face datasets
from app.chunking.registry import ChunkerRegistry
from app.indexing.embedder import Embedder
from app.indexing.vector_store import VectorStore

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
    local_file = os.path.join(base_dir, "data", "raw", "hintrain.parquet")
    print(f"Loading local dataset from {local_file}...")
    if not os.path.exists(local_file):
        raise FileNotFoundError(f"Local dataset file not found at {local_file}")
        
    print("Reading parquet file...")
    parquet_file = pq.ParquetFile(local_file)
    dataset = []
    for batch in parquet_file.iter_batches():
        dataset.extend(batch.to_pylist())

    batch_size = 5000
    batch_chunks = []
    batch_metadatas = []
    total_embedded = 0

    for idx, item in enumerate(dataset):
        passages_dict = item.get('passages', {})
        translated_passages = passages_dict.get('Translated_passages', [])
        
        if not translated_passages:
            continue
            
        text = "\n\n".join(translated_passages)
        answer = item.get('Answer', '').strip()
        if answer:
            text = f"Answer: {answer}\n\nPassages:\n{text}"
            
        if not text.strip():
            continue
        
        chunks = chunker.chunk(text, metadata=item)
        batch_chunks.extend(chunks)
        batch_metadatas.extend([item] * len(chunks))
        
        if len(batch_chunks) >= batch_size:
            print(f"Embedding batch of {len(batch_chunks)} chunks... Total processed docs: {idx}")
            embeddings = embedder.embed(batch_chunks)
            print("Adding batch to vector store...")
            vector_store.add_texts(batch_chunks, embeddings=embeddings, metadatas=batch_metadatas)
            total_embedded += len(batch_chunks)
            batch_chunks = []
            batch_metadatas = []

    # Process remaining chunks
    if batch_chunks:
        print(f"Embedding final batch of {len(batch_chunks)} chunks...")
        embeddings = embedder.embed(batch_chunks)
        print("Adding final batch to vector store...")
        vector_store.add_texts(batch_chunks, embeddings=embeddings, metadatas=batch_metadatas)
        total_embedded += len(batch_chunks)

    print(f"Total chunks embedded: {total_embedded}")
    
    print("Persisting...")
    vector_store.persist()
    print("Index built successfully!")

if __name__ == "__main__":
    build_index()