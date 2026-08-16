import chromadb
import os
import hashlib
import sqlite3
import time

def get_dir_size(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total += os.path.getsize(fp)
    return total

persist_directory = r"D:\rag-in-goa\data\chroma_db"
sqlite_path = os.path.join(persist_directory, "chroma.sqlite3")
wal_path = sqlite_path + "-wal"

print(f"--- INIT ---")
print(f"Initial disk size: {get_dir_size(persist_directory) / (1024*1024):.2f} MB")

client = chromadb.PersistentClient(path=persist_directory)
collections = client.list_collections()
collection_name = collections[0].name if collections else "msmarco_xi_passages"
collection = client.get_collection(name=collection_name)
initial_count = collection.count()

print(f"Initial chunk count: {initial_count}")

# 1. Deduplication
print(f"\n--- STEP 1: Deduplication ---")
batch_size = 5000
offset = 0

doc_hashes = {}
canonical_ids = {} # hash -> id
to_delete = []
to_update_ids = []
to_update_metadatas = []

while offset < initial_count:
    data = collection.get(limit=batch_size, offset=offset, include=["documents", "metadatas"])
    ids = data["ids"]
    docs = data["documents"]
    metas = data["metadatas"]
    
    if not ids:
        break
        
    for i in range(len(ids)):
        doc = docs[i]
        doc_id = ids[i]
        meta = metas[i] or {}
        
        # In case the doc is somehow missing
        if not doc:
            continue
            
        h = hashlib.sha256(doc.encode('utf-8')).hexdigest()
        
        if h in doc_hashes:
            # Duplicate found
            to_delete.append(doc_id)
            
            # Merge query_id into the canonical one
            can_id = canonical_ids[h]
            can_meta = doc_hashes[h]
            
            # Extract existing query_ids
            existing_qids = can_meta.get("query_ids", str(can_meta.get("query_id", "")))
            new_qid = str(meta.get("query_id", ""))
            
            if new_qid and new_qid not in existing_qids.split(","):
                merged_qids = f"{existing_qids},{new_qid}".strip(",")
                can_meta["query_ids"] = merged_qids
                doc_hashes[h] = can_meta
                
                # We need to keep track of updates
                if can_id not in to_update_ids:
                    to_update_ids.append(can_id)
                    to_update_metadatas.append(can_meta)
                else:
                    idx = to_update_ids.index(can_id)
                    to_update_metadatas[idx] = can_meta
        else:
            canonical_ids[h] = doc_id
            doc_hashes[h] = meta
            
    offset += batch_size

print(f"Found {len(to_delete)} duplicates out of {initial_count}.")

if to_delete:
    print(f"Deleting {len(to_delete)} duplicate chunks...")
    # Delete in batches to avoid limits
    del_batch = 5000
    for i in range(0, len(to_delete), del_batch):
        collection.delete(ids=to_delete[i:i+del_batch])

if to_update_ids:
    print(f"Updating metadata for {len(to_update_ids)} canonical chunks...")
    upd_batch = 5000
    for i in range(0, len(to_update_ids), upd_batch):
        collection.update(
            ids=to_update_ids[i:i+upd_batch],
            metadatas=to_update_metadatas[i:i+upd_batch]
        )

post_dedup_count = collection.count()
print(f"Chunks remaining after dedup: {post_dedup_count}")

# Close Chroma client so we don't hold sqlite locks
client = None

print(f"Disk size after dedup: {get_dir_size(persist_directory) / (1024*1024):.2f} MB")

# 2. Check redundant embedding storage
print(f"\n--- STEP 2: Check Redundant Embedding Storage ---")
try:
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM embeddings")
    emb_count = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(LENGTH(embedding)) FROM embeddings")
    emb_bytes = cursor.fetchone()[0] or 0
    print(f"SQLite 'embeddings' table contains {emb_count} rows, taking {emb_bytes / (1024*1024):.2f} MB of raw blob space.")
    if emb_count > 0:
        print("YES, Chroma is storing embeddings redundantly in the SQLite DB in addition to the HNSW index files.")
    conn.close()
except Exception as e:
    print(f"Error checking sqlite embeddings: {e}")

# 3. Vacuum
print(f"\n--- STEP 3: Vacuum ---")
sqlite_size = os.path.getsize(sqlite_path) if os.path.exists(sqlite_path) else 0
wal_size = os.path.getsize(wal_path) if os.path.exists(wal_path) else 0
print(f"Before vacuum: chroma.sqlite3 = {sqlite_size / (1024*1024):.2f} MB, -wal = {wal_size / (1024*1024):.2f} MB")

try:
    conn = sqlite3.connect(sqlite_path)
    conn.isolation_level = None
    cursor = conn.cursor()
    cursor.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    cursor.execute("VACUUM")
    conn.close()
except Exception as e:
    print(f"Vacuum error: {e}")

sqlite_size_after = os.path.getsize(sqlite_path) if os.path.exists(sqlite_path) else 0
wal_size_after = os.path.getsize(wal_path) if os.path.exists(wal_path) else 0
print(f"After vacuum: chroma.sqlite3 = {sqlite_size_after / (1024*1024):.2f} MB, -wal = {wal_size_after / (1024*1024):.2f} MB")

final_disk_size = get_dir_size(persist_directory)
print(f"Disk size after vacuum: {final_disk_size / (1024*1024):.2f} MB")

