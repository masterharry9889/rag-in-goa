import time
import requests
from app.graph.state import GraphState
from app.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_groq_api(prompt: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": settings.groq_model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant answering questions based on the provided context in Hindi. Answer accurately."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=20.0)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def generate(state: GraphState) -> GraphState:
    """
    Generate node. Calls LLM with retrieved context to answer the user query.
    """
    start_time = time.time()
    
    query = state.get("text_query") or state.get("transcribed_text")
    context = "\n\n".join(state.get("retrieved_texts", []))
    
    if not query:
        state["generated_answer"] = "No query provided."
        return state
        
    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer in Hindi based strictly on the context above:"
    
    try:
        answer = call_groq_api(prompt)
    except Exception as e:
        answer = "क्षमा करें, मुझे उत्तर उत्पन्न करने में त्रुटि हुई।"  # Error in generating answer
        
    latency = (time.time() - start_time) * 1000
    
    if "latency_trace" not in state:
        state["latency_trace"] = {}
        
    state["latency_trace"]["generate"] = latency
    state["generated_answer"] = answer
    
    return state
