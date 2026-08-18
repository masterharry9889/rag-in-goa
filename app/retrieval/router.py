from app.retrieval.hybrid_retriever import HybridRetriever
from typing import List, Dict, Any

class RetrievalRouter:
    def __init__(self):
        # We can initialize different retrievers here if needed
        self.default_retriever = HybridRetriever(top_k=3)
        
    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        Routes the query to the appropriate retrieval strategy.
        Currently defaults to HybridRetriever.
        """
        # In a more advanced implementation, we could classify the query
        # and route to different retrievers (e.g., metadata filters vs pure dense)
        return self.default_retriever.retrieve(query)

retrieval_router = RetrievalRouter()
