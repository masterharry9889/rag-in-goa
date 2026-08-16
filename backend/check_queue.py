import sqlite3
import os

persist_directory = r"D:\rag-in-goa\data\chroma_db"
sqlite_path = os.path.join(persist_directory, "chroma.sqlite3")

conn = sqlite3.connect(sqlite_path)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*), SUM(LENGTH(vector)) FROM embeddings_queue")
row = cursor.fetchone()
print(f"embeddings_queue rows: {row[0]}, vector bytes: {row[1]}")

conn.close()
