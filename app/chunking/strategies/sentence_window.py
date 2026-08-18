import hashlib
from typing import List, Dict, Any
from app.chunking.schema import Chunk

class SentenceWindowChunker:
    def __init__(self, window_size: int = 2):
        self.window_size = window_size

    def _split_into_sentences(self, text: str) -> List[str]:
        import re
        sentences = re.split(r'(?<=[।?!.])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk(self, text: str, source_doc_id: str, base_metadata: Dict[str, Any]) -> List[Chunk]:
        sentences = self._split_into_sentences(text)
        chunks = []
        
        for i, sentence in enumerate(sentences):
            # The core text to embed is just the sentence itself
            # But the metadata contains the full window context for the generator
            
            start_idx = max(0, i - self.window_size)
            end_idx = min(len(sentences), i + self.window_size + 1)
            window_context = " ".join(sentences[start_idx:end_idx])
            
            chunk_id = hashlib.sha256(f"{source_doc_id}_window_{i}".encode()).hexdigest()
            
            metadata = base_metadata.copy()
            metadata["position"] = i
            # Important: Store full context in metadata so it can be retrieved
            # But the vector DB indexes `text` (which is just the sentence)
            metadata["window_context"] = window_context
            
            chunks.append(Chunk(
                id=chunk_id,
                text=sentence,
                source_doc_id=source_doc_id,
                strategy="sentence_window",
                token_count=len(sentence.split()),
                metadata=metadata
            ))
            
        return chunks
