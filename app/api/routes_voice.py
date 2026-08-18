from fastapi import APIRouter, File, UploadFile, Request, HTTPException
from fastapi.responses import JSONResponse
from app.graph.state import GraphState
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()

class QueryResponse(BaseModel):
    answer: str
    citations: Optional[List[Dict[str, Any]]] = None
    latency_trace: Optional[Dict[str, float]] = None

@router.post("/query", response_model=QueryResponse)
async def query_voice(request: Request, file: UploadFile = File(...)):
    if not file.filename.endswith(('.wav', '.mp3', '.m4a', '.ogg')):
        raise HTTPException(status_code=400, detail="Invalid audio format.")
    
    audio_data = await file.read()
    
    initial_state: GraphState = {
        "audio_data": audio_data,
        "text_query": None,
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
        logging.error(f"Error processing voice query: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
