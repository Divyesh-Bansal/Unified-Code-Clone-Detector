"""
Cosine Similarity Module (TF-IDF)

Computes cosine similarity between two token lists using TF-IDF weighting.
Used by LexicalDetector.

IDF scheme (2-document corpus):
  idf(t) = 1 + log(2 / df(t))
  - Token in both methods:  df=2  → idf = 1 + log(1) = 1.0
  - Token in one method:    df=1  → idf = 1 + log(2) ≈ 1.693

TF is computed as  freq(t, doc) / total_tokens(doc)  (standard term frequency).
Each weight w(t, doc) = tf(t, doc) * idf(t), then standard cosine is applied.
"""

import math
from typing import Dict, List

from my_tool.tokenizer import Token

# IDF values for the 2-document (2-method) corpus
_IDF_SHARED = 1.0           # token appears in both methods: 1 + log(2/2)
_IDF_UNIQUE = 1.0 + math.log(2)  # token appears in one method only: 1 + log(2/1)


def cosine_similarity(tokens_a: List[Token], tokens_b: List[Token]) -> float:
    """
    Compute the TF-IDF cosine similarity between two token lists.

    Each token is weighted by TF-IDF where TF = freq / total_tokens and
    IDF distinguishes tokens shared between both methods (weight 1.0) from
    tokens unique to one method (weight ≈ 1.693).  The dot product of the
    resulting TF-IDF vectors, divided by their magnitudes, gives the cosine.

    Args:
        tokens_a: First method's token list.
        tokens_b: Second method's token list.

    Returns:
        Similarity percentage (0-100).
    """
    if not tokens_a or not tokens_b:
        return 0.0

    # Build raw frequency maps
    freq_a = _build_frequency_map(tokens_a)
    freq_b = _build_frequency_map(tokens_b)

    # Total token counts (use for TF denominator, not vocab size)
    total_a = len(tokens_a)
    total_b = len(tokens_b)

    # Union of all unique token texts
    all_tokens = set(freq_a.keys()) | set(freq_b.keys())

    dot_product = 0.0
    magnitude_a = 0.0
    magnitude_b = 0.0

    for token in all_tokens:
        # Raw frequencies (0 if absent)
        fa = freq_a.get(token, 0.0)
        fb = freq_b.get(token, 0.0)

        # TF: frequency / total tokens in that method
        tf_a = fa / total_a if fa > 0 else 0.0
        tf_b = fb / total_b if fb > 0 else 0.0

        # IDF: shared tokens vs. unique-to-one tokens
        idf = _IDF_SHARED if (fa > 0 and fb > 0) else _IDF_UNIQUE

        # TF-IDF weighted components
        w_a = tf_a * idf
        w_b = tf_b * idf

        dot_product += w_a * w_b
        magnitude_a += w_a * w_a
        magnitude_b += w_b * w_b

    denom = math.sqrt(magnitude_a) * math.sqrt(magnitude_b)
    if denom == 0:
        return 0.0

    return (dot_product / denom) * 100.0


def _build_frequency_map(tokens: List[Token]) -> Dict[str, float]:
    """Build a token text -> raw count map."""
    freq: Dict[str, float] = {}
    for token in tokens:
        text = token.value
        freq[text] = freq.get(text, 0.0) + 1.0
    return freq
