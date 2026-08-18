import time
from typing import Dict, Any
from app.graph.state import GraphState
from app.retrieval.router import retrieval_router

def retrieve(state: GraphState) -> GraphState:
    """
    Retrieve node. Executes the retrieval logic and measures retrieval latency.
    """
    start_time = time.time()
    
    query = state.get("text_query")
    if not query and state.get("transcribed_text"):
        query = state.get("transcribed_text")
        
    if not query:
        state["chunks"] = []
        state["retrieved_texts"] = []
        return state
        
    chunks = retrieval_router.retrieve(query)
    retrieved_texts = [chunk["text"] for chunk in chunks]
    
    latency = (time.time() - start_time) * 1000  # in ms
    
    if "latency_trace" not in state:
        state["latency_trace"] = {}
    
    state["latency_trace"]["retrieve"] = latency
    state["chunks"] = chunks
    state["retrieved_texts"] = retrieved_texts
    
    return state
