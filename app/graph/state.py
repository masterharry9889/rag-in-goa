from typing_extensions import TypedDict
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class GraphState(TypedDict):
    # Input from client
    audio_data: Optional[bytes]  # For voice query
    text_query: Optional[str]    # For text query (if provided directly or after STT)
    
    # STT result
    transcribed_text: Optional[str]
    
    # Chunking and retrieval
    chunks: Optional[List[dict]]  # Retrieved chunks with metadata
    retrieved_texts: Optional[List[str]]  # Text of retrieved chunks
    
    # Generation
    generated_answer: Optional[str]
    
    # Guardrails
    input_guard_passed: Optional[bool]
    output_guard_passed: Optional[bool]
    refusal_reason: Optional[str]
    
    # Output
    final_answer: Optional[str]
    citations: Optional[List[dict]]
    
    # Latency tracing (optional, for debugging)
    latency_trace: Optional[dict]