from chunking.base import ChunkerStrategy
from chunking.fixed_size import FixedSizeChunker
from chunking.semantic import SemanticChunker
from chunking.recursive import RecursiveChunker
from chunking.metadata_aware import MetadataAwareChunker
from chunking.sentence_window import SentenceWindowChunker
from typing import List, Dict, Type

class ChunkerRegistry:
    _strategies: Dict[str, Type[ChunkerStrategy]] = {
        "fixed_size": FixedSizeChunker,
        "semantic": SemanticChunker,
        "recursive": RecursiveChunker,
        "metadata_aware": MetadataAwareChunker,
        "sentence_window": SentenceWindowChunker,
    }

    @classmethod
    def get_strategy(cls, strategy_name: str, **kwargs) -> ChunkerStrategy:
        if strategy_name not in cls._strategies:
            raise ValueError(f"Unknown chunking strategy: {strategy_name}")
        return cls._strategies[strategy_name](**kwargs)

    @classmethod
    def list_strategies(cls) -> List[str]:
        return list(cls._strategies.keys())

    @classmethod
    def select_strategy_for_query(cls, query: str, doc_type: str = None) -> str:
        # Simple heuristic for strategy selection
        # In practice, this could be more sophisticated
        if doc_type == "faq":
            return "sentence_window"
        elif len(query.split()) > 10:  # Longer queries might benefit from semantic chunking
            return "semantic"
        else:
            return "fixed_size"  # Default fallback