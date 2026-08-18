import time
from app.graph.state import GraphState
from app.stt.sarvam_client import sarvam_client

def input_guard(state: GraphState) -> GraphState:
    """
    Input guard node. Transcribes audio if present and classifies input.
    """
    start_time = time.time()
    
    if state.get("audio_data") and not state.get("text_query"):
        try:
            transcript = sarvam_client.transcribe(state["audio_data"])
            state["transcribed_text"] = transcript
            query = transcript
        except Exception:
            state["input_guard_passed"] = False
            state["refusal_reason"] = "Audio transcription failed."
            return state
    else:
        query = state.get("text_query")

    if not query or not query.strip():
        state["input_guard_passed"] = False
        state["refusal_reason"] = "Empty query."
    else:
        # Simple heuristic check for off-topic or unsafe content could go here
        # E.g. prompt injection detection or checking for unsafe keywords.
        # We will assume it passes by default for this hackathon context.
        state["input_guard_passed"] = True
        
    latency = (time.time() - start_time) * 1000
    if "latency_trace" not in state:
        state["latency_trace"] = {}
    state["latency_trace"]["input_guard"] = latency
    
    return state
