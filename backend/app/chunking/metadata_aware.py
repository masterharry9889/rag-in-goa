from chunking.base import ChunkerStrategy
from typing import List, Dict

class MetadataAwareChunker(ChunkerStrategy):
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str, metadata: dict = None) -> list[str]:
        # If metadata contains section information, we can split by section first
        # For simplicity, we'll just use fixed-size chunking but tag each chunk with metadata
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            # In a real implementation, we would attach metadata to each chunk
            # For now, we just return the text chunks
            chunks.append(chunk_text)
            start = end - self.chunk_overlap
        return chunks