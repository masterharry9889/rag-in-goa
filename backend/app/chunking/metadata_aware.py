from app.chunking.base import ChunkerStrategy
from typing import List, Dict

class MetadataAwareChunker(ChunkerStrategy):
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50, align_to_passage: bool = True):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.align_to_passage = align_to_passage

    def chunk(self, text: str, metadata: dict = None) -> list[str]:
        if self.align_to_passage and "Passages:" in text:
            # Simple assumption: passages are separated by \n\n
            parts = text.split("Passages:\n")
            if len(parts) > 1:
                passages_text = parts[1]
                # split by double newline
                passages = passages_text.split("\n\n")
                
                # if there is an Answer section
                prefix = parts[0] + "Passages:\n"
                
                chunks = []
                for p in passages:
                    if p.strip():
                        chunks.append(prefix + p.strip())
                return chunks

        # Fallback to fixed size
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            chunks.append(chunk_text)
            start = end - self.chunk_overlap
        return chunks