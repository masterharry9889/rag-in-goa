import sqlite3
import os

persist_directory = r"D:\rag-in-goa\data\chroma_db"
sqlite_path = os.path.join(persist_directory, "chroma.sqlite3")

conn = sqlite3.connect(sqlite_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

sizes = []
for table in tables:
    name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {name}")
    count = cursor.fetchone()[0]
    cursor.execute(f"PRAGMA page_count;")
    page_count_before = cursor.fetchone()[0]
    # To really get table size in sqlite without dbstat, we just report rows.
    # But we can get bytes of text for document table?
    # the documents are in embedding_fulltext_search?
    
    # Let's check embeddings_queue, embeddings, embedding_metadata, embedding_fulltext_search_data
    # Actually, let's just query dbstat if available
    
try:
    cursor.execute("SELECT name, sum(pgsize) FROM dbstat GROUP BY name ORDER BY sum(pgsize) DESC LIMIT 10;")
    stats = cursor.fetchall()
    print("Table sizes (bytes):")
    for row in stats:
        print(f"  {row[0]}: {row[1]} bytes ({row[1]/(1024*1024):.2f} MB)")
except Exception as e:
    print("dbstat not available:", e)

conn.close()
