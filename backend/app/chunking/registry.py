from app.chunking.base import ChunkerStrategy
from app.chunking.fixed_size import FixedSizeChunker
from app.chunking.semantic import SemanticChunker
from app.chunking.recursive import RecursiveChunker
from app.chunking.metadata_aware import MetadataAwareChunker
from app.chunking.sentence_window import SentenceWindowChunker
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
        
        import inspect
        strategy_cls = cls._strategies[strategy_name]
        
        # Map common arguments
        if 'overlap' in kwargs:
            kwargs['chunk_overlap'] = kwargs['overlap']
        if 'chunk_size' in kwargs:
            kwargs['max_chunk_size'] = kwargs['chunk_size']
            
        sig = inspect.signature(strategy_cls.__init__)
        valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        
        return strategy_cls(**valid_kwargs)

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