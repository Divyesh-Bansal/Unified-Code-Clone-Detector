"""
Longest Common Subsequence (LCS) Module — IDF-Weighted

Computes LCS-based similarity between two token lists, where each
matched token contributes its **IDF weight** instead of a flat +1.

IDF scheme (2-document corpus, same as cosine module):
  idf(t) = 1 + log(2 / df(t))
  - Token in both methods:  df=2  → idf = 1.0
  - Token in one method:    df=1  → idf ≈ 1.693

This means matching a rare custom identifier contributes ~1.7× more
than matching common boilerplate like `for`, `int`, `=`, etc.

The final score is normalised against the maximum possible weighted
score (the sum of IDF weights for the shorter method) so the result
stays in the 0-100% range.
"""

import math
from typing import Dict, List, Set

from my_tool.tokenizer import Token

# IDF values for the 2-document (2-method) corpus
_IDF_SHARED = 1.0                  # token appears in both methods
_IDF_UNIQUE = 1.0 + math.log(2)   # token appears in one method only


def _compute_idf_weights(tokens_a: List[Token],
                         tokens_b: List[Token]) -> Dict[str, float]:
    """
    Build IDF weights from a 2-document corpus (the two methods).

    Returns a dict mapping each unique token value → its IDF weight.
    """
    vocab_a: Set[str] = {t.value for t in tokens_a}
    vocab_b: Set[str] = {t.value for t in tokens_b}

    all_tokens = vocab_a | vocab_b
    weights: Dict[str, float] = {}

    for tok in all_tokens:
        in_a = tok in vocab_a
        in_b = tok in vocab_b
        if in_a and in_b:
            weights[tok] = _IDF_SHARED
        else:
            weights[tok] = _IDF_UNIQUE

    return weights


def lcs_similarity(tokens_a: List[Token], tokens_b: List[Token]) -> float:
    """
    Compute the IDF-weighted LCS similarity between two token lists.

    Uses a two-row dynamic programming algorithm.  When two tokens match,
    the cell value increases by the token's IDF weight (not a flat +1).
    The result is normalised against the maximum possible weighted score.

    Args:
        tokens_a: First method's token list.
        tokens_b: Second method's token list.

    Returns:
        Similarity percentage (0-100).
    """
    if not tokens_a or not tokens_b:
        return 0.0

    m = len(tokens_a)
    n = len(tokens_b)

    # Compute IDF weights from the 2-method corpus
    idf = _compute_idf_weights(tokens_a, tokens_b)

    # Keep the shorter sequence as the column axis to minimise memory
    if m < n:
        tokens_a, tokens_b = tokens_b, tokens_a
        m, n = n, m

    # prev_row[j] = weighted LCS score for tokens_a[:i-1] vs tokens_b[:j]
    prev_row = [0.0] * (n + 1)

    for i in range(1, m + 1):
        curr_row = [0.0] * (n + 1)
        for j in range(1, n + 1):
            if tokens_a[i - 1].value == tokens_b[j - 1].value:
                w = idf.get(tokens_a[i - 1].value, 1.0)
                curr_row[j] = prev_row[j - 1] + w       # diagonal + weight
            else:
                curr_row[j] = max(prev_row[j], curr_row[j - 1])  # skip
        prev_row = curr_row

    weighted_lcs = prev_row[n]

    # Maximum possible score = sum of IDF weights for the shorter method
    # (tokens_b after the possible swap is the shorter one)
    max_score = sum(idf.get(t.value, 1.0) for t in tokens_b)
    if max_score == 0:
        return 0.0

    return (weighted_lcs / max_score) * 100.0
