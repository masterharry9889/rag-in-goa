# Refusal templates for when the system cannot or should not answer a query.

REFUSAL_TEMPLATES = [
    "I don't have enough grounded information to answer that question.",
    "I cannot provide an answer based on the available context.",
    "The information needed to answer that question is not present in the retrieved context.",
    "I'm unable to answer that question as it may be unsafe or off-topic.",
    "I don't have sufficient information to provide a reliable answer.",
]

def get_refusal_template(index: int = 0) -> str:
    """Return a refusal template by index."""
    if 0 <= index < len(REFUSAL_TEMPLATES):
        return REFUSAL_TEMPLATES[index]
    return REFUSAL_TEMPLATES[0]