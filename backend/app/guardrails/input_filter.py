# Basic keyword-based input filter for safety and topic relevance

# List of blocked terms for safety check (extend as needed)
BLOCKED_TERMS = {
    'violence', 'hate', 'harassment', 'illegal', 'self-harm',
    'sexual', 'porn', 'weapon', 'drug'
}

# Default expected topics if none provided (extend as needed)
DEFAULT_EXPECTED_TOPICS = {
    'technology', 'science', 'history', 'culture', 'business',
    'politics', 'health', 'education'
}

def is_input_safe(query: str) -> bool:
    """
    Check if the input is safe (not unsafe/inappropriate).
    Returns False if any blocked term is found in the query (case-insensitive).
    """
    query_lower = query.lower()
    return not any(term in query_lower for term in BLOCKED_TERMS)

import numpy as np

# A handful of representative domain queries (Hindi and general knowledge)
DOMAIN_QUERIES = [
    "भारत के प्रधानमंत्री कौन हैं?",
    "ताजमहल कहाँ स्थित है?",
    "हिन्दी भाषा का इतिहास क्या है?",
    "विज्ञान के क्षेत्र में भारत का योगदान",
    "कंप्यूटर कैसे काम करता है?",
    "what is the capital of india",
    "how to cook rice",
]

_DOMAIN_EMBEDDINGS = None

def get_domain_embeddings(embedder):
    global _DOMAIN_EMBEDDINGS
    if _DOMAIN_EMBEDDINGS is None:
        _DOMAIN_EMBEDDINGS = np.array(embedder.embed(DOMAIN_QUERIES))
    return _DOMAIN_EMBEDDINGS

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def is_input_on_topic(query: str, embedder, threshold: float = 0.20) -> bool:
    """
    Check if the input is on-topic using embedding similarity.
    Returns True if similarity >= threshold.
    """
    domain_embeds = get_domain_embeddings(embedder)
    query_embed = np.array(embedder.embed_query(query))
    
    similarities = [cosine_similarity(query_embed, d_emb) for d_emb in domain_embeds]
    max_sim = max(similarities) if similarities else 0.0
    
    return max_sim >= threshold