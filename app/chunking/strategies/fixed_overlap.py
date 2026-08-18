import hashlib
from typing import List, Dict, Any
from app.chunking.schema import Chunk

class FixedOverlapChunker:
    def __init__(self, chunk_size: int = 256, overlap: int = 48):
        self.chunk_size = chunk_size
        self.overlap = overlap
        # Using a simple word-based tokenizer for speed in this example
        # Real implementation would use tiktoken or sentencepiece matching the LLM/embedder

    def _tokenize(self, text: str) -> List[str]:
        return text.split()
        
    def _detokenize(self, tokens: List[str]) -> str:
        return " ".join(tokens)

    def chunk(self, text: str, source_doc_id: str, base_metadata: Dict[str, Any]) -> List[Chunk]:
        tokens = self._tokenize(text)
        chunks = []
        
        if not tokens:
            return chunks

        step = self.chunk_size - self.overlap
        if step <= 0:
            step = 1

        offset = 0
        while offset < len(tokens):
            chunk_tokens = tokens[offset:offset + self.chunk_size]
            chunk_text = self._detokenize(chunk_tokens)
            
            chunk_id = hashlib.sha256(f"{source_doc_id}_fixed_overlap_{offset}".encode()).hexdigest()
            
            metadata = base_metadata.copy()
            metadata["position"] = offset
            
            chunks.append(Chunk(
                id=chunk_id,
                text=chunk_text,
                source_doc_id=source_doc_id,
                strategy="fixed_overlap",
                token_count=len(chunk_tokens),
                metadata=metadata
            ))
            
            offset += step
            
        return chunks
