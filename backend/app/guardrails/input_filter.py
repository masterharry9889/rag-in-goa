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

def is_input_on_topic(query: str, expected_topics: list = None) -> bool:
    """
    Check if the input is on-topic.
    Returns True if any of the expected topics is found in the query (case-insensitive).
    If expected_topics is None, uses DEFAULT_EXPECTED_TOPICS.
    """
    if expected_topics is None:
        expected_topics = DEFAULT_EXPECTED_TOPICS
    query_lower = query.lower()
    return any(topic.lower() in query_lower for topic in expected_topics)