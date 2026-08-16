import chromadb
import os

persist_directory = r"D:\rag-in-goa\data\chroma_db"
client = chromadb.PersistentClient(path=persist_directory)

# List collections
collections = client.list_collections()
collection_name = collections[0].name if collections else "msmarco_xi_passages"
print(f"Collection Name: {collection_name}")

collection = client.get_collection(name=collection_name)
count = collection.count()
print(f"Total Chunks: {count}")

if count > 0:
    # Fetch some items to get embedding dim and sample text
    # We will fetch up to 1000 items to check for duplicates and average length
    sample_size = min(count, 5000)
    data = collection.get(limit=sample_size, include=["embeddings", "documents", "metadatas"])
    
    embeddings = data.get("embeddings")
    documents = data.get("documents")
    metadatas = data.get("metadatas")
    
    emb_dim = len(embeddings[0]) if embeddings is not None and len(embeddings) > 0 else 0
    print(f"Embedding Dimension: {emb_dim}")
    
    # Calculate average chunk size in chars
    total_chars = sum(len(doc) for doc in documents) if documents else 0
    avg_chars = total_chars / len(documents) if documents else 0
    print(f"Average Chunk Size (chars): {avg_chars:.2f}")
    
    # Check deduplication
    unique_docs = set(documents)
    print(f"Unique documents in sample: {len(unique_docs)} out of {len(documents)}")
    dedup_applied = len(unique_docs) == len(documents)
    print(f"Deduplication Applied: {'Yes' if dedup_applied else 'No'}")
    
    # Check is_selected filter
    # Look at the metadatas or the total count
    # Usually msmarco has 7-8M passages. If count is ~65k or 100k, it's filtered.
    is_selected_applied = count < 1_000_000
    print(f"is_selected filter applied: {'Yes' if is_selected_applied else 'No'}")
    
    # Raw vector size
    raw_size_bytes = count * emb_dim * 4
    print(f"Raw Vector Size: {raw_size_bytes} bytes ({raw_size_bytes / (1024*1024):.2f} MB)")
else:
    print("Collection is empty.")
