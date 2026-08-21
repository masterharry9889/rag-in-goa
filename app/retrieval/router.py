from app.retrieval.hybrid_retriever import HybridRetriever
from app.config import settings
from typing import List, Dict, Any


class RetrievalRouter:
    def __init__(self):
        # top_k is driven by settings so it can be tuned via .env without code changes
        self.default_retriever = HybridRetriever(top_k=settings.retrieval_top_k)

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        Routes the query to the appropriate retrieval strategy.
        Currently defaults to HybridRetriever (dense vector search via ChromaDB).
        """
        return self.default_retriever.retrieve(query)


retrieval_router = RetrievalRouter()
