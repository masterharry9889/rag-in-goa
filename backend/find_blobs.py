import sqlite3
import os

persist_directory = r"D:\rag-in-goa\data\chroma_db"
sqlite_path = os.path.join(persist_directory, "chroma.sqlite3")

conn = sqlite3.connect(sqlite_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

for table in tables:
    name = table[0]
    cursor.execute(f"PRAGMA table_info({name});")
    columns = cursor.fetchall()
    has_blob = any('BLOB' in col[2] for col in columns)
    if has_blob:
        print(f"Table {name} has BLOB columns:")
        for col in columns:
            if 'BLOB' in col[2]:
                print(f"  - {col[1]} ({col[2]})")
conn.close()
