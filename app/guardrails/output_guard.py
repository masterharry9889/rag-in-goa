import time
from app.graph.state import GraphState
from app.guardrails.refusal_templates import HALLUCINATION_REFUSAL

def output_guard(state: GraphState) -> GraphState:
    """
    Output guard node. Checks groundedness of generated answer against retrieved context.
    """
    start_time = time.time()
    
    # If it already failed input guard, bypass
    if state.get("input_guard_passed") is False:
        return state
        
    answer = state.get("generated_answer")
    
    if not answer:
        state["output_guard_passed"] = False
        state["refusal_reason"] = "Empty answer generated."
        return state
        
    # Heuristic groundedness check: simple length check or keyword overlap
    # In a real implementation this could be an LLM call or NLI model
    # For now, we assume it's grounded if it's not an error message
    if "क्षमा करें" in answer and "त्रुटि" in answer:
        state["output_guard_passed"] = False
        state["refusal_reason"] = HALLUCINATION_REFUSAL
    else:
        state["output_guard_passed"] = True
        
    latency = (time.time() - start_time) * 1000
    if "latency_trace" not in state:
        state["latency_trace"] = {}
    state["latency_trace"]["output_guard"] = latency
    
    return state
