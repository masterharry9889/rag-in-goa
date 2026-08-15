from typing import Dict, Any
import time
import os
from stt.base import STTBase
from stt.sarvam_client import SarvamClient
from stt.elevenlabs_client import ElevenLabsClient
from chunking.registry import ChunkerRegistry
from retrieval.retriever import Retriever
from retrieval.reranker import Reranker
from generation.prompt_templates import PROMPT_TEMPLATE
from generation.llm_client import LLMClient
from observability.latency_logger import LatencyLogger
from indexing.embedder import Embedder
from indexing.vector_store import VectorStore

# Initialize components (in practice, these would be dependency injected)
stt_provider = os.getenv("STT_PROVIDER", "sarvam")  # or from config
if stt_provider == "sarvam":
    stt_client = SarvamClient()
else:
    stt_client = ElevenLabsClient()

# Initialize embedder and vector store
embedder = Embedder()
vector_store_path = os.getenv("VECTOR_DB_PATH", "./data/processed/vector_db")
# Try to load the vector store, if it doesn't exist, we'll create a new one (but note: we need to have built it first)
if os.path.exists(f"{vector_store_path}.index") and os.path.exists(f"{vector_store_path}_texts.json"):
    vector_store = VectorStore()
    vector_store.load(vector_store_path)
else:
    # If the vector store doesn't exist, we'll create an empty one and note that it needs to be built.
    # In a real application, we might want to build it on startup or have a separate script.
    vector_store = VectorStore()
    # We could also build it here, but for now we'll just leave it empty and note that it needs to be built.
    print(f"Warning: Vector store not found at {vector_store_path}. Please run the build_index script first.")

retriever = Retriever(vector_store) if vector_store else None
reranker = Reranker()
llm_client = LLMClient()  # Uses environment variables for provider and API key
latency_logger = LatencyLogger()

async def stt_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node for speech-to-text transcription."""
    start_time = time.time()
    try:
        # In a real scenario, state would contain audio_data
        # For now, we assume state has 'audio_data' key
        audio_data = state.get("audio_data")
        if not audio_data:
            raise ValueError("No audio data provided")
        
        transcript = await stt_client.transcribe(audio_data)
        latency = (time.time() - start_time) * 1000
        latency_logger.log("stt", latency)
        
        return {
            "transcript": transcript,
            "latency_ms": state.get("latency_ms", 0) + latency
        }
    except Exception as e:
        return {
            "error": f"STT failed: {str(e)}",
            "latency_ms": state.get("latency_ms", 0) + (time.time() - start_time) * 1000
        }

async def retrieve_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node for retrieving relevant chunks."""
    start_time = time.time()
    try:
        query = state.get("transcript", "")
        if not query:
            raise ValueError("No query to retrieve")
        
        # Retrieve chunks
        chunks = retriever.retrieve(query) if retriever else []
        
        # Optional reranking
        if reranker and chunks:
            chunks = reranker.rerank(query, chunks, top_k=5)
        
        latency = (time.time() - start_time) * 1000
        latency_logger.log("retrieval", latency)
        
        return {
            "chunks": chunks,
            "latency_ms": state.get("latency_ms", 0) + latency
        }
    except Exception as e:
        return {
            "error": f"Retrieval failed: {str(e)}",
            "latency_ms": state.get("latency_ms", 0) + (time.time() - start_time) * 1000
        }

async def guardrails_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node for running guardrails on input and retrieved context."""
    start_time = time.time()
    try:
        query = state.get("transcript", "")
        chunks = state.get("chunks", [])
        
        # Placeholder for actual guardrail logic
        # In practice, we would check:
        # 1. Input filter: is the query on-topic and safe?
        # 2. Grounding check: are the chunks relevant to the query?
        # 3. Hallucination check: (usually done after generation, but we can do a preliminary check)
        
        # For now, we just pass through and set a flag if we should refuse
        # We'll assume we have a function to check if the query is safe and on-topic
        is_safe = True  # Placeholder
        is_on_topic = True  # Placeholder
        
        if not is_safe or not is_on_topic:
            # We can set a flag to refuse answering
            return {
                "should_refuse": True,
                "refusal_reason": "Query is unsafe or off-topic",
                "latency_ms": state.get("latency_ms", 0) + (time.time() - start_time) * 1000
            }
        
        latency = (time.time() - start_time) * 1000
        latency_logger.log("guardrails", latency)
        
        return {
            "latency_ms": state.get("latency_ms", 0) + latency
        }
    except Exception as e:
        return {
            "error": f"Guardrails failed: {str(e)}",
            "latency_ms": state.get("latency_ms", 0) + (time.time() - start_time) * 1000
        }

async def generation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node for generating the answer."""
    start_time = time.time()
    try:
        query = state.get("transcript", "")
        chunks = state.get("chunks", [])
        
        if not chunks:
            # If no chunks, we might want to refuse or use a fallback
            return {
                "answer": "I don't have enough information to answer that question.",
                "latency_ms": state.get("latency_ms", 0) + (time.time() - start_time) * 1000
            }
        
        # Prepare context from chunks
        context = "\n\n".join(chunks[:5])  # Use top 5 chunks
        
        # Format the prompt
        prompt = PROMPT_TEMPLATE.format(context=context, question=query)
        
        # Generate the answer using the LLM client
        answer = llm_client.generate(prompt)
        
        latency = (time.time() - start_time) * 1000
        latency_logger.log("generation", latency)
        
        return {
            "answer": answer,
            "latency_ms": state.get("latency_ms", 0) + latency
        }
    except Exception as e:
        return {
            "error": f"Generation failed: {str(e)}",
            "latency_ms": state.get("latency_ms", 0) + (time.time() - start_time) * 1000
        }