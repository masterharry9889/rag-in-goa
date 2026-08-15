"""
Offline script to build the vector index from a dataset.
Steps:
1. Load dataset (e.g., from Hugging Face or local files)
2. Chunk the documents using a selected chunking strategy
3. Embed the chunks
4. Add to vector store and persist
"""
import os
from typing import List, Dict, Any, Optional
from datasets import load_dataset  # Assuming we use Hugging Face datasets
from chunking.registry import ChunkerRegistry
from indexing.embedder import Embedder
from indexing.vector_store import VectorStore

def build_index(
    dataset_name: str = "ai4bharat/MSMARCO-XI",
    split: str = "train",
    chunking_strategy: str = "semantic",
    embedder: Embedder = None,
    vector_store: VectorStore = None,
    persist_path: str = "./data/processed/vector_db",
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    limit: int = None,  # Limit number of documents for testing
    dataset: Optional[Any] = None  # If provided, use this dataset instead of downloading
):
    # Initialize chunker
    chunker = ChunkerRegistry.get_strategy(
        chunking_strategy,
        chunk_size=chunk_size,
        overlap=chunk_overlap
    )
    
    # If dataset is not provided, download from HF
    if dataset is None:
        print(f"Loading dataset {dataset_name}...")
        dataset = load_dataset(dataset_name, split=split)
    if limit:
        dataset = dataset.select(range(limit))
    
    # Process each document
    all_chunks = []
    all_metadatas = []
    for idx, item in enumerate(dataset):
        # Assuming the dataset has a 'text' field; adjust as needed
        text = item.get('text', '')
        if not text:
            continue
        
        # Chunk the text
        chunks = chunker.chunk(text, metadata=item)
        all_chunks.extend(chunks)
        # For each chunk, store metadata (we can store the original item or parts of it)
        all_metadatas.extend([item] * len(chunks))
        
        if idx % 100 == 0:
            print(f"Processed {idx} documents, {len(all_chunks)} chunks so far")
    
    print(f"Total chunks: {len(all_chunks)}")
    
    # Initialize embedder and vector store if not provided
    if embedder is None:
        embedder = Embedder()
    if vector_store is None:
        vector_store = VectorStore()
    
    # Embed chunks
    print("Embedding chunks...")
    embeddings = embedder.embed(all_chunks)
    
    # Add to vector store
    print("Adding to vector store...")
    vector_store.add_texts(all_chunks, metadatas=all_metadatas)
    
    # Persist
    print(f"Persisting vector store to {persist_path}...")
    vector_store.persist(persist_path)
    print("Index built successfully!")

if __name__ == "__main__":
    # This is a placeholder; in practice, we would inject concrete embedder and vector store
    # For example, using SentenceTransformer embedder and FAISS vector store
    # We'll just call the function with default parameters to build the index.
    build_index()