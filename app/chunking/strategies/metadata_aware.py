import hashlib
from typing import List, Dict, Any
from app.chunking.schema import Chunk

class MetadataAwareChunker:
    def __init__(self, max_tokens: int = 512):
        self.max_tokens = max_tokens

    def chunk(self, text: str, source_doc_id: str, base_metadata: Dict[str, Any]) -> List[Chunk]:
        # This strategy relies on the source data being pre-split into passages
        # MSMARCO dataset has 'passage_id' which we want to respect
        # Instead of splitting arbitrarily, we just ensure the passage is within bounds
        # If it's too long, we do a very basic split, but mostly we leave it intact.
        
        tokens = text.split()
        chunks = []
        
        if len(tokens) <= self.max_tokens:
            chunk_id = hashlib.sha256(f"{source_doc_id}_metadata_0".encode()).hexdigest()
            metadata = base_metadata.copy()
            metadata["position"] = 0
            
            chunks.append(Chunk(
                id=chunk_id,
                text=text,
                source_doc_id=source_doc_id,
                strategy="metadata_aware",
                token_count=len(tokens),
                metadata=metadata
            ))
        else:
            # Fallback for extremely long passages, split into 2
            mid = len(tokens) // 2
            for i, part_tokens in enumerate([tokens[:mid], tokens[mid:]]):
                part_text = " ".join(part_tokens)
                chunk_id = hashlib.sha256(f"{source_doc_id}_metadata_{i}".encode()).hexdigest()
                metadata = base_metadata.copy()
                metadata["position"] = i
                
                chunks.append(Chunk(
                    id=chunk_id,
                    text=part_text,
                    source_doc_id=source_doc_id,
                    strategy="metadata_aware",
                    token_count=len(part_tokens),
                    metadata=metadata
                ))
                
        return chunks
