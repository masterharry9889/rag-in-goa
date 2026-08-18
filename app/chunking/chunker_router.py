from typing import List, Dict, Any
from app.chunking.schema import Chunk
from app.chunking.strategies.fixed_overlap import FixedOverlapChunker
from app.chunking.strategies.semantic_split import SemanticSplitChunker
from app.chunking.strategies.sentence_window import SentenceWindowChunker
from app.chunking.strategies.metadata_aware import MetadataAwareChunker

class ChunkerRouter:
    def __init__(self):
        self.strategies = {
            "fixed_overlap": FixedOverlapChunker(),
            "semantic": SemanticSplitChunker(),
            "sentence_window": SentenceWindowChunker(),
            "metadata_aware": MetadataAwareChunker()
        }

    def chunk(self, text: str, source_doc_id: str, base_metadata: Dict[str, Any], active_strategies: List[str] = None) -> List[Chunk]:
        """
        Runs the text through specified chunking strategies.
        Defaults to metadata_aware and semantic for indexing as requested.
        """
        if active_strategies is None:
            active_strategies = ["metadata_aware", "semantic"]
            
        all_chunks = []
        for strategy_name in active_strategies:
            if strategy_name in self.strategies:
                strategy = self.strategies[strategy_name]
                chunks = strategy.chunk(text, source_doc_id, base_metadata)
                all_chunks.extend(chunks)
                
        return all_chunks

chunker_router = ChunkerRouter()
