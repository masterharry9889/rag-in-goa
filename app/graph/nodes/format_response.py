import json
from pydantic import BaseModel, ValidationError
from typing import List, Optional
from app.graph.state import GraphState

class FinalResponseSchema(BaseModel):
    answer: str
    citations: Optional[List[dict]] = []

def format_response(state: GraphState) -> GraphState:
    """
    Validates final output against Pydantic schema.
    If guardrails failed, formats a refusal response.
    """
    if state.get("input_guard_passed") is False or state.get("output_guard_passed") is False:
        state["final_answer"] = state.get("refusal_reason", "Request could not be processed.")
        state["citations"] = []
        return state
        
    answer = state.get("generated_answer", "")
    citations = state.get("chunks", [])
    
    # Simple formatting validation logic
    # In a real app we might ask LLM to output JSON and validate it.
    # Here we just wrap it into the schema to ensure it matches expectations.
    try:
        formatted = FinalResponseSchema(answer=answer, citations=citations)
        state["final_answer"] = formatted.answer
        state["citations"] = formatted.citations
    except ValidationError:
        # Fallback mechanism
        state["final_answer"] = "क्षमा करें, उत्तर को सही स्वरूप में नहीं लाया जा सका।"
        state["citations"] = []
        
    return state
