from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.graph.state import GraphState
from fastapi.responses import JSONResponse

router = APIRouter()

class TextQueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    citations: Optional[List[Dict[str, Any]]] = None
    latency_trace: Optional[Dict[str, float]] = None

@router.post("/query", response_model=QueryResponse)
async def query_text(request: Request, body: TextQueryRequest):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Empty query provided.")
    
    initial_state: GraphState = {
        "audio_data": None,
        "text_query": body.query,
        "transcribed_text": None,
        "chunks": None,
        "retrieved_texts": None,
        "generated_answer": None,
        "input_guard_passed": None,
        "output_guard_passed": None,
        "refusal_reason": None,
        "final_answer": None,
        "citations": None,
        "latency_trace": {}
    }
    
    try:
        graph = request.app.state.graph
        result = graph.invoke(initial_state)
        
        return QueryResponse(
            answer=result.get("final_answer", "No answer generated."),
            citations=result.get("citations"),
            latency_trace=result.get("latency_trace")
        )
    except Exception as e:
        import logging
        logging.error(f"Error processing text query: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})
