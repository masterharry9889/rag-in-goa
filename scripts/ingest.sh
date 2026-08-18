#!/bin/bash
set -e

echo "Starting ingestion pipeline..."

# Ensure we are in the project root
export PYTHONPATH="."

echo "Step 1: Building Index (Download, Chunk, Embed, Upsert)"
python app/ingestion/build_index.py

echo "Step 2: Pruning Index (Deduplication)"
python app/ingestion/prune_index.py

echo "Step 3: Database Size Check"
echo "ChromaDB size on disk:"
du -sh data/chroma/

echo "Ingestion complete."
