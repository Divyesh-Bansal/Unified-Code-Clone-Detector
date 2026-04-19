"""
Cosine Similarity Module (N-Gram TF-IDF)

Computes cosine similarity between two token lists using TF-IDF weighting
over **trigrams** (sequences of 3 consecutive token values).  This injects
"local ordering" into the score — `A = B` and `B = A` now have different
trigram profiles and are no longer considered identical.

Graceful fallback: if a method has fewer than 3 tokens, bigrams are tried,
then unigrams — so very short methods still produce valid scores.

IDF scheme (2-document corpus):
  idf(t) = 1 + log(2 / df(t))
  - Trigram in both methods:  df=2  → idf = 1 + log(1) = 1.0
  - Trigram in one method:    df=1  → idf = 1 + log(2) ≈ 1.693

TF is computed as  freq(gram, doc) / total_grams(doc)  (standard term freq).
Each weight w(g, doc) = tf(g, doc) * idf(g), then standard cosine is applied.
"""

import math
from typing import Dict, List, Tuple

from my_tool.tokenizer import Token

# IDF values for the 2-document (2-method) corpus
_IDF_SHARED = 1.0           # gram appears in both methods: 1 + log(2/2)
_IDF_UNIQUE = 1.0 + math.log(2)  # gram appears in one method only: 1 + log(2/1)


def cosine_similarity(tokens_a: List[Token], tokens_b: List[Token]) -> float:
    """
    Compute the TF-IDF cosine similarity between two token lists.

    Builds **trigram** frequency maps from each token stream, computes TF-IDF
    over those trigrams, and returns the cosine similarity of the resulting
    vectors.  Falls back to bigrams or unigrams for very short methods.

    Args:
        tokens_a: First method's token list.
        tokens_b: Second method's token list.

    Returns:
        Similarity percentage (0-100).
    """
    if not tokens_a or not tokens_b:
        return 0.0

    # Pick the largest n that gives at least 1 gram from both sides
    min_len = min(len(tokens_a), len(tokens_b))
    n = 3
    if min_len < 3:
        n = 2 if min_len >= 2 else 1

    # Build n-gram frequency maps
    freq_a = _build_ngram_frequency_map(tokens_a, n)
    freq_b = _build_ngram_frequency_map(tokens_b, n)

    total_a = sum(freq_a.values())
    total_b = sum(freq_b.values())

    if total_a == 0 or total_b == 0:
        return 0.0

    # Union of all unique grams
    all_grams = set(freq_a.keys()) | set(freq_b.keys())

    dot_product = 0.0
    magnitude_a = 0.0
    magnitude_b = 0.0

    for gram in all_grams:
        # Raw frequencies (0 if absent)
        fa = freq_a.get(gram, 0.0)
        fb = freq_b.get(gram, 0.0)

        # TF: frequency / total grams in that method
        tf_a = fa / total_a if fa > 0 else 0.0
        tf_b = fb / total_b if fb > 0 else 0.0

        # IDF: shared grams vs. unique-to-one grams
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


def _build_ngram_frequency_map(tokens: List[Token],
                                n: int) -> Dict[Tuple[str, ...], float]:
    """
    Build an n-gram frequency map from a token list.

    Each n-gram is a tuple of `n` consecutive token values.
    Returns a dict mapping each n-gram → its raw count.
    """
    freq: Dict[Tuple[str, ...], float] = {}
    values = [t.value for t in tokens]
    for i in range(len(values) - n + 1):
        gram = tuple(values[i:i + n])
        freq[gram] = freq.get(gram, 0.0) + 1.0
    return freq
