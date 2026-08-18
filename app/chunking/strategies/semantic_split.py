import hashlib
import numpy as np
from typing import List, Dict, Any
from app.chunking.schema import Chunk
from app.retrieval.embedder import embedder

class SemanticSplitChunker:
    def __init__(self, threshold: float = 0.75, max_tokens: int = 384):
        self.threshold = threshold
        self.max_tokens = max_tokens

    def _split_into_sentences(self, text: str) -> List[str]:
        # Simple heuristic for Hindi/English sentence splitting
        import re
        sentences = re.split(r'(?<=[।?!.])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk(self, text: str, source_doc_id: str, base_metadata: Dict[str, Any]) -> List[Chunk]:
        sentences = self._split_into_sentences(text)
        if not sentences:
            return []
            
        # Embed all sentences
        embeddings = embedder.embed_texts(sentences)
        
        chunks = []
        current_chunk_sentences = [sentences[0]]
        current_chunk_token_count = len(sentences[0].split())
        
        for i in range(1, len(sentences)):
            # Cosine similarity between consecutive sentences
            vec1 = np.array(embeddings[i-1])
            vec2 = np.array(embeddings[i])
            # normalize for cosine similarity
            sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-10)
            
            sentence_tokens = len(sentences[i].split())
            
            if sim < self.threshold or current_chunk_token_count + sentence_tokens > self.max_tokens:
                # Boundary detected, save current chunk
                chunk_text = " ".join(current_chunk_sentences)
                chunk_id = hashlib.sha256(f"{source_doc_id}_semantic_{len(chunks)}".encode()).hexdigest()
                
                metadata = base_metadata.copy()
                metadata["position"] = len(chunks)
                
                chunks.append(Chunk(
                    id=chunk_id,
                    text=chunk_text,
                    source_doc_id=source_doc_id,
                    strategy="semantic",
                    token_count=current_chunk_token_count,
                    metadata=metadata
                ))
                
                current_chunk_sentences = [sentences[i]]
                current_chunk_token_count = sentence_tokens
            else:
                # Add to current chunk
                current_chunk_sentences.append(sentences[i])
                current_chunk_token_count += sentence_tokens
                
        # Flush remaining
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunk_id = hashlib.sha256(f"{source_doc_id}_semantic_{len(chunks)}".encode()).hexdigest()
            
            metadata = base_metadata.copy()
            metadata["position"] = len(chunks)
            
            chunks.append(Chunk(
                id=chunk_id,
                text=chunk_text,
                source_doc_id=source_doc_id,
                strategy="semantic",
                token_count=current_chunk_token_count,
                metadata=metadata
            ))
            
        return chunks
