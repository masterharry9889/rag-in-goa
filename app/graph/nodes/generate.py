import logging
import time
import requests
from app.graph.state import GraphState
from app.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# System prompt that strictly grounds the LLM in the retrieved context.
# The model is instructed to explicitly say it doesn't know if context is insufficient.
_SYSTEM_PROMPT = """You are a precise Hindi-language assistant for the MSMARCO-XI dataset.

RULES (follow strictly):
1. Answer ONLY using information contained in the CONTEXT section below.
2. Respond entirely in Hindi.
3. If the context does not contain enough information to answer the question, respond with exactly:
   "मुझे खेद है, लेकिन दिए गए डेटाबेस में इस प्रश्न का उत्तर उपलब्ध नहीं है।"
4. Do NOT use your own training knowledge or make up facts.
5. Cite the relevant passage when possible.
6. Be concise and factual."""


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_groq_api(context: str, question: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    user_message = f"""CONTEXT:
{context}

QUESTION: {question}

Answer in Hindi strictly based on the CONTEXT above:"""

    payload = {
        "model": settings.groq_model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.1,  # Low temperature for factual grounding
        "max_tokens": 512,
    }

    logger.info("[CHAT] AI request started — model=%s", settings.groq_model)
    logger.debug("[RAG] Full user message sent to Groq:\n%s", user_message[:800])

    response = requests.post(url, headers=headers, json=payload, timeout=20.0)
    response.raise_for_status()
    data = response.json()
    answer = data["choices"][0]["message"]["content"]
    logger.info("[CHAT] AI response received — length=%d chars", len(answer))
    return answer


def generate(state: GraphState) -> GraphState:
    """
    Generate node. Calls Groq LLM with strictly retrieved context.

    Early-exits with a 'not found in database' message when no relevant
    chunks were retrieved, preventing LLM from falling back to its own knowledge.
    """
    start_time = time.time()

    query = state.get("text_query") or state.get("transcribed_text")
    retrieved_texts: list = state.get("retrieved_texts") or []
    chunks: list = state.get("chunks") or []

    if not query:
        state["generated_answer"] = "कोई प्रश्न नहीं दिया गया।"
        return state

    # ── Guard: no context retrieved ──────────────────────────────────────────
    if not retrieved_texts:
        logger.warning(
            "[RAG] Zero chunks retrieved for query %r — returning 'not in DB' answer "
            "without calling Groq, to prevent hallucination.",
            query[:80],
        )
        state["generated_answer"] = (
            "मुझे खेद है, लेकिन दिए गए डेटाबेस में इस प्रश्न का उत्तर उपलब्ध नहीं है।"
        )
        state["latency_trace"] = state.get("latency_trace", {})
        state["latency_trace"]["generate"] = (time.time() - start_time) * 1000
        return state

    # ── Build context block with chunk scores ─────────────────────────────────
    context_parts = []
    for i, (text, chunk) in enumerate(zip(retrieved_texts, chunks), start=1):
        score = chunk.get("score", "?")
        passage_id = chunk.get("metadata", {}).get("passage_id", "?")
        context_parts.append(f"[Passage {i} | id={passage_id} | score={score}]\n{text}")
    context = "\n\n---\n\n".join(context_parts)

    logger.debug(
        "[RAG] Injecting %d chunks into Groq prompt (total context ~%d chars).",
        len(retrieved_texts),
        len(context),
    )
    logger.debug("[RAG] Context being sent:\n%s", context[:1000])

    # ── Call Groq ─────────────────────────────────────────────────────────────
    try:
        answer = call_groq_api(context=context, question=query)
    except Exception:
        logger.exception("[CHAT] Groq AI generation failed")
        answer = "क्षमा करें, मुझे उत्तर उत्पन्न करने में त्रुटि हुई।"

    latency = (time.time() - start_time) * 1000

    if "latency_trace" not in state:
        state["latency_trace"] = {}

    state["latency_trace"]["generate"] = latency
    state["generated_answer"] = answer

    return state
