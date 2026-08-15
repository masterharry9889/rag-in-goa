from chunking.base import ChunkerStrategy
from typing import List, Dict

class SemanticChunker(ChunkerStrategy):
    def __init__(self, max_chunk_size: int = 512):
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str, metadata: dict = None) -> list[str]:
        # Simple semantic chunking: split by paragraphs (double newline)
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        for para in paragraphs:
            # If adding this paragraph would exceed max size, finalize current chunk and start new
            if len(current_chunk) + len(para) > self.max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks