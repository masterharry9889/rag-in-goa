from pydantic import BaseModel
from typing import Literal, Dict, Any

class Chunk(BaseModel):
    id: str  # deterministic hash of (source_id, strategy, offset)
    text: str
    source_doc_id: str
    strategy: Literal["fixed_overlap", "semantic", "sentence_window", "metadata_aware"]
    token_count: int
    metadata: Dict[str, Any]  # passage_id, query_id, lang, position
