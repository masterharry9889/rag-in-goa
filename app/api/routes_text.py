import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.graph.state import GraphState
from fastapi.responses import JSONResponse

router = APIRouter()
logger = logging.getLogger(__name__)

class TextQueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    citations: Optional[List[Dict[str, Any]]] = None
    latency_trace: Optional[Dict[str, float]] = None

@router.post("/query", response_model=QueryResponse)
async def query_text(request: Request, body: TextQueryRequest):
    logger.info("[CHAT] backend request received: text query")
    if not body.query.strip():
        logger.warning("[CHAT] rejected empty text query")
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
        logger.info("[CHAT] AI request started")
        graph = request.app.state.graph
        result = graph.invoke(initial_state)
        response = QueryResponse(
            answer=result.get("final_answer", "No answer generated."),
            citations=result.get("citations"),
            latency_trace=result.get("latency_trace")
        )
        logger.info("[CHAT] response returned")
        return response
    except Exception as e:
        logger.exception("[CHAT] backend error while processing text query")
        return JSONResponse(status_code=500, content={"detail": str(e)})
