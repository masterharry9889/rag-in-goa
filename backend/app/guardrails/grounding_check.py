# Simple grounding check based on word overlap (excluding stopwords)

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

def is_grounded(answer: str, chunks: list[str]) -> bool:
    """
    Check if the answer is grounded in the retrieved chunks.
    We consider it grounded if at least 30% of the unique words in the answer
    appear in the chunks (after removing stopwords).
    """
    if not answer.strip():
        return False

    answer_words = _get_words(answer)
    if not answer_words:
        # If answer has no meaningful words, we cannot check grounding
        return True

    # Combine all chunks into one string and get words
    chunks_text = ' '.join(chunks)
    chunks_words = _get_words(chunks_text)

    # Compute overlap
    common_words = answer_words & chunks_words
    overlap_ratio = len(common_words) / len(answer_words)

    return overlap_ratio >= 0.3