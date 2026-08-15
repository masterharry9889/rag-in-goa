# Simple hallucination check based on word overlap (inverse of grounding)

import re

# A small set of English stopwords
STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were',
    'will', 'with'
}

def _get_words(text):
    """Return a set of words from text, lowercased, without stopwords and punctuation."""
    words = re.findall(r'\b\w+\b', text.lower())
    return {word for word in words if word not in STOPWORDS}

def is_hallucinated(answer: str, chunks: list[str]) -> bool:
    """
    Check if the answer is hallucinated (not supported by the chunks).
    We consider it hallucinated if less than 30% of the unique words in the answer
    appear in the chunks (after removing stopwords).
    """
    if not answer.strip():
        # Empty answer is considered hallucinated (no information provided)
        return True

    answer_words = _get_words(answer)
    if not answer_words:
        # If answer has no meaningful words, we cannot check for hallucination
        # Assume not hallucinated (since there's no false information)
        return False

    # Combine all chunks into one string and get words
    chunks_text = ' '.join(chunks)
    chunks_words = _get_words(chunks_text)

    # Compute overlap
    common_words = answer_words & chunks_words
    overlap_ratio = len(common_words) / len(answer_words)

    # Hallucinated if overlap is below threshold
    return overlap_ratio < 0.3