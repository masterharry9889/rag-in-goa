from typing import TypedDict, List, Dict, Any, Optional

class GraphState(TypedDict):
    """Represents the state of our graph."""
    query: str  # The user's query (after STT)
    transcript: str  # The raw transcript from STT
    chunks: List[str]  # The retrieved chunks
    answer: str  # The generated answer
    error: Optional[str]  # Any error that occurred
    retry_count: int  # Number of retries for the current node
    latency_ms: float  # Total latency so far