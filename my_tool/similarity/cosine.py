"""
Cosine Similarity Module (TF-IDF)

Computes cosine similarity between two token lists using TF-IDF weighting.
Used by LexicalDetector.
"""

import math
from typing import Dict, List

from my_tool.tokenizer import Token


def cosine_similarity(tokens_a: List[Token], tokens_b: List[Token]) -> float:
    """
    Compute the TF-IDF cosine similarity between two token lists.

    Uses term frequency normalized by vocabulary size, with IDF weighting:
    - Tokens appearing in only one list get IDF = 1.6931472 (1 + log(2/1))
    - Tokens appearing in both lists get IDF = 1.0 (1 + log(2/2))

    Args:
        tokens_a: First method's token list.
        tokens_b: Second method's token list.

    Returns:
        Similarity percentage (0-100).
    """
    if not tokens_a or not tokens_b:
        return 0.0

    # Build frequency maps
    freq_a = _build_frequency_map(tokens_a)
    freq_b = _build_frequency_map(tokens_b)

    # Calculate TF (frequency / vocabulary size)
    tf_a: Dict[str, float] = {k: v / len(freq_a) for k, v in freq_a.items()}
    tf_b: Dict[str, float] = {k: v / len(freq_b) for k, v in freq_b.items()}

    # Get union of all tokens
    all_tokens = set(tf_a.keys()) | set(tf_b.keys())

    # Calculate TF-IDF weighted cosine similarity
    dot_product = 0.0
    magnitude_a = 0.0
    magnitude_b = 0.0

    idf_unique = 1.6931472  # 1 + log(2/1) — token in only one method
    # idf_shared = 1.0       # 1 + log(2/2) — token in both methods

    for token in all_tokens:
        v1 = tf_a.get(token, 0.0)
        v2 = tf_b.get(token, 0.0)

        # Apply IDF weighting
        if v1 > 0 and token not in tf_b:
            v1 *= idf_unique
        if v2 > 0 and token not in tf_a:
            v2 *= idf_unique

        dot_product += v1 * v2
        magnitude_a += v1 * v1
        magnitude_b += v2 * v2

    # Avoid division by zero
    denom = math.sqrt(magnitude_a) * math.sqrt(magnitude_b)
    if denom == 0:
        return 0.0

    cosine = dot_product / denom
    return cosine * 100.0


def _build_frequency_map(tokens: List[Token]) -> Dict[str, float]:
    """Build a token text -> frequency count map."""
    freq: Dict[str, float] = {}
    for token in tokens:
        text = token.value
        freq[text] = freq.get(text, 0.0) + 1.0
    return freq
