from fastapi import APIRouter, HTTPException, File, UploadFile
from app.api.schemas import VoiceQueryResponse
import base64
from app.harness.graph import create_rag_graph

router = APIRouter()

# Create the RAG graph once
app_graph = create_rag_graph()

@router.post("/voice-query", response_model=VoiceQueryResponse)
async def voice_query(audio: UploadFile = File(...)):
    try:
        # Read the raw audio bytes from the uploaded file
        audio_data = await audio.read()
        
        # Initialize the state
        initial_state = {
            "audio_data": audio_data,
            "query": "",  # Will be filled by STT
            "transcript": "",
            "chunks": [],
            "answer": "",
            "error": None,
            "retry_count": 0,
            "latency_ms": 0.0,
            "should_refuse": False
        }
        
        # Run the graph
        final_state = await app_graph.ainvoke(initial_state)
        
        # Check for errors
        if final_state.get("error"):
            print("Final state error:", repr(final_state["error"]))
            raise HTTPException(status_code=500, detail=final_state["error"])
        
        # Return the response
        return VoiceQueryResponse(
            transcript=final_state.get("transcript", ""),
            answer=final_state.get("answer", ""),
            latency_ms=final_state.get("latency_ms", 0.0)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Exception: {str(e)}")