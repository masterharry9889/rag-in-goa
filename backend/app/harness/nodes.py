from typing import Dict, Any
import time
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
from app.stt.base import STTBase
from app.stt.sarvam_client import SarvamClient
from app.stt.elevenlabs_client import ElevenLabsClient
from app.chunking.registry import ChunkerRegistry
from app.retrieval.retriever import Retriever
from app.retrieval.reranker import Reranker
from app.generation.prompt_templates import PROMPT_TEMPLATE
from app.generation.llm_client import LLMClient
from app.observability.latency_logger import LatencyLogger
from app.indexing.embedder import Embedder
# Guardrails imports
from app.guardrails.input_filter import is_input_safe, is_input_on_topic
from app.guardrails.grounding_check import is_grounded
from app.guardrails.hallucination_check import is_hallucinated
from app.guardrails.refusal_templates import get_refusal_template
# Retry policy
from .retry_policy import retry_with_backoff

# Initialize components (in practice, these would be dependency injected)
stt_provider = os.getenv("STT_PROVIDER", "sarvam")
if stt_provider == "sarvam":
    stt_client = SarvamClient()
else:
    stt_client = ElevenLabsClient()
if not getattr(stt_client, "client", None):
    stt_client = None

import yaml
import chromadb
from app.indexing.chroma_store import ChromaStore

# Initialize embedder and vector store
embedder = Embedder()
vector_store_path = os.getenv("VECTOR_DB_PATH", "./data/chroma_db")

# Read config for collection name and thresholds
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.yaml")
collection_name = "msmarco_xi_passages"
domain_centroid_threshold = 0.20
try:
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        collection_name = config.get("retrieval", {}).get("vector_db", {}).get("collection_name", collection_name)
        domain_centroid_threshold = config.get("guardrails", {}).get("input_filter", {}).get("domain_centroid_threshold", domain_centroid_threshold)
except Exception:
    pass

vector_store = ChromaStore(persist_directory=vector_store_path, collection_name=collection_name)

# Check if collection has elements to throw a warning
try:
    if vector_store.collection.count() == 0:
        print(f"Warning: Vector store collection '{collection_name}' is empty. Please run the build_index script first.")
except Exception:
    print(f"Warning: Vector store collection '{collection_name}' not accessible. Please run the build_index script first.")

retriever = Retriever(vector_store, embedder)

reranker = Reranker()
llm_client = LLMClient()  # Uses environment variables for provider and API key
latency_logger = LatencyLogger()

async def stt_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node for speech-to-text transcription."""
    if state.get("should_refuse", False) or state.get("error"):
        return state
    start_time = time.time()
    try:
        audio_data = state.get("audio_data")
        if not audio_data:
            raise ValueError("No audio data provided")

        if stt_client is None:
            transcript = "Demo mode: no STT API key configured."
            latency = (time.time() - start_time) * 1000
            latency_logger.log("stt", latency)
            return {
                "transcript": transcript,
                "latency_ms": state.get("latency_ms", 0) + latency
            }

        @retry_with_backoff
        async def _transcribe_with_retry():
            return await stt_client.transcribe(audio_data)

        transcript = await _transcribe_with_retry()

        latency = (time.time() - start_time) * 1000
        latency_logger.log("stt", latency)

        if not transcript or not transcript.strip():
            state["should_refuse"] = True
            state["refusal_reason"] = "No speech detected"
            state["refusal_guardrail"] = "stt_node"
            state["answer"] = "I couldn't hear any speech. Please try again."
            return {
                "should_refuse": True,
                "refusal_reason": "No speech detected",
                "refusal_guardrail": "stt_node",
                "answer": "I couldn't hear any speech. Please try again.",
                "transcript": "",
                "latency_ms": state.get("latency_ms", 0) + latency
            }

        return {
            "transcript": transcript,
            "latency_ms": state.get("latency_ms", 0) + latency
        }
    except Exception as e:
        return {
            "error": f"STT failed: {str(e)}",
            "latency_ms": state.get("latency_ms", 0) + (time.time() - start_time) * 1000
        }

def get_chunk_texts(chunks: list) -> list:
    """Helper to extract text from chunk dictionaries."""
    if not chunks: return []
    if isinstance(chunks[0], dict):
        return [c.get("text", "") for c in chunks]
    return chunks

async def retrieve_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node for retrieving relevant chunks."""
    if state.get("should_refuse", False) or state.get("error"):
        return state
    start_time = time.time()
    try:
        query = state.get("transcript", "")
        if not query:
            raise ValueError("No query to retrieve")
        
        chunks = retriever.retrieve(query) if retriever else []

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
            "chunks": [],
            "latency_ms": state.get("latency_ms", 0) + (time.time() - start_time) * 1000
        }

async def guardrails_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Node for running guardrails on input and retrieved context."""
    if state.get("should_refuse", False) or state.get("error"):
        return state
    start_time = time.time()
    try:
        query = state.get("transcript", "")
        chunks = state.get("chunks", [])
        
        # 1. Input filter
        is_safe = is_input_safe(query)
        is_on_topic = is_input_on_topic(query, embedder, domain_centroid_threshold)
        if not is_safe or not is_on_topic:
            if not is_safe and not is_on_topic:
                reason = "Query is unsafe and off-topic"
            elif not is_safe:
                reason = "Query is unsafe"
            else:
                reason = "Query is off-topic"
            state["should_refuse"] = True
            state["refusal_reason"] = reason
            state["refusal_guardrail"] = "input_filter"
            state["answer"] = get_refusal_template()
            latency = (time.time() - start_time) * 1000
            latency_logger.log("guardrails", latency)
            return state
        
        # 2. Grounding check: check if the query is grounded in the chunks (as a proxy for relevance)
        # We use the query as the answer in the grounding check to see if the chunks support the query.
        chunk_strs = get_chunk_texts(chunks)
        if not is_grounded(query, chunk_strs):
            state["should_refuse"] = True
            state["refusal_reason"] = "Retrieved chunks do not support answering the query"
            state["refusal_guardrail"] = "grounding_check"
            state["answer"] = get_refusal_template()
            latency = (time.time() - start_time) * 1000
            latency_logger.log("guardrails", latency)
            return state
        
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
    if state.get("should_refuse", False) or state.get("error"):
        return state
    start_time = time.time()
    try:
        query = state.get("transcript", "")
        chunks = state.get("chunks", [])
        
        if not chunks:
            state["answer"] = (
                "Demo mode: no relevant chunks were returned, so the backend is currently running without "
                "live retrieval or generation credentials."
            )
            latency = (time.time() - start_time) * 1000
            latency_logger.log("generation", latency)
            return {
                "answer": state["answer"],
                "latency_ms": state.get("latency_ms", 0) + latency
            }

        chunk_strs = get_chunk_texts(chunks)
        context = "\n\n".join(chunk_strs[:5])
        prompt = PROMPT_TEMPLATE.format(context=context, question=query)

        @retry_with_backoff
        def _generate_with_retry(prompt):
            return llm_client.generate(prompt)

        try:
            answer = _generate_with_retry(prompt)
        except Exception:
            answer = (
                "Demo mode: the LLM API key is not configured, so the app is returning a local fallback response."
            )

        if llm_client and llm_client.client and is_hallucinated(answer, chunk_strs):
            state["should_refuse"] = True
            state["refusal_reason"] = "Answer is hallucinated (not supported by the retrieved chunks)"
            state["refusal_guardrail"] = "hallucination_check"
            state["answer"] = get_refusal_template()
        else:
            state["answer"] = answer

        latency = (time.time() - start_time) * 1000
        latency_logger.log("generation", latency)
        return {
            "answer": state.get("answer"),
            "latency_ms": state.get("latency_ms", 0) + latency
        }
    except Exception as e:
        return {
            "error": f"Generation failed: {str(e)}",
            "latency_ms": state.get("latency_ms", 0) + (time.time() - start_time) * 1000
        }