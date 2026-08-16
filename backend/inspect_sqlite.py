import sqlite3
import os

persist_directory = r"D:\rag-in-goa\data\chroma_db"
sqlite_path = os.path.join(persist_directory, "chroma.sqlite3")

conn = sqlite3.connect(sqlite_path)
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='embeddings';")
schema = cursor.fetchone()
print(schema[0] if schema else "No embeddings table found.")

cursor.execute("PRAGMA table_info(embeddings);")
columns = cursor.fetchall()
print("Columns:", columns)
conn.close()
