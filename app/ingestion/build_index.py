import os
import pandas as pd
from tqdm import tqdm
import time
import hashlib
from app.config import settings
from app.ingestion.download_dataset import download_hinval_dataset
from app.chunking.chunker_router import chunker_router
from app.retrieval.chroma_client import chroma_db
from app.retrieval.embedder import embedder

def build_index():
    # 1. Download
    file_path = download_hinval_dataset()
    
    # 2. Read dataset (we might need to install pyarrow or fastparquet)
    print(f"Loading parquet from {file_path}...")
    df = pd.read_parquet(file_path)
    
    # Limit corpus size for the hackathon
    total_docs = min(len(df), settings.max_indexed_passages)
    df = df.head(total_docs)
    
    print(f"Processing {total_docs} rows...")
    
    collection = chroma_db.collection
    
    batch_size = 64
    docs_batch = []
    meta_batch = []
    ids_batch = []
    
    # Simple deduplication set
    seen_content_hashes = set()
    
    for idx, row in tqdm(df.iterrows(), total=total_docs):
        # Data format of MSMARCO-XI: we assume query_id, passage_id, text, etc.
        # Fallback to general column names if exact schema isn't known
        text = str(row.get("text", row.get("passage", "")))
        passage_id = str(row.get("passage_id", idx))
        query_id = str(row.get("query_id", ""))
        
        if not text:
            continue
            
        base_meta = {
            "passage_id": passage_id,
            "query_id": query_id,
            "lang": "hi"
        }
        
        chunks = chunker_router.chunk(text, source_doc_id=passage_id, base_metadata=base_meta)
        
        for chunk in chunks:
            # Deduplicate by content hash before writing
            content_hash = hashlib.sha256(chunk.text.encode()).hexdigest()
            if content_hash in seen_content_hashes:
                continue
            seen_content_hashes.add(content_hash)
            
            docs_batch.append(chunk.text)
            meta_batch.append({
                "strategy": chunk.strategy,
                "passage_id": chunk.metadata.get("passage_id", ""),
                "position": chunk.metadata.get("position", 0)
                # avoid storing full text here to save space
            })
            ids_batch.append(chunk.id)
            
            if len(docs_batch) >= batch_size:
                # Embed batch
                embeddings = embedder.embed_texts(docs_batch)
                
                # Write to Chroma
                collection.upsert(
                    ids=ids_batch,
                    documents=docs_batch,
                    embeddings=embeddings,
                    metadatas=meta_batch
                )
                
                docs_batch = []
                meta_batch = []
                ids_batch = []
                
    # Flush remaining
    if docs_batch:
        embeddings = embedder.embed_texts(docs_batch)
        collection.upsert(
            ids=ids_batch,
            documents=docs_batch,
            embeddings=embeddings,
            metadatas=meta_batch
        )
        
    print(f"Index built successfully. Unique chunks indexed: {len(seen_content_hashes)}")

if __name__ == "__main__":
    build_index()
