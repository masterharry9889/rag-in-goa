from app.chunking.base import ChunkerStrategy
from typing import List, Dict

class SentenceWindowChunker(ChunkerStrategy):
    def __init__(self, window_size: int = 3):
        self.window_size = window_size

    def chunk(self, text: str, metadata: dict = None) -> list[str]:
        # Split text into sentences (simple split by ., !, ?)
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        for i in range(len(sentences)):
            start = max(0, i - self.window_size)
            end = min(len(sentences), i + self.window_size + 1)
            window = sentences[start:end]
            chunks.append(' '.join(window))
        return chunks