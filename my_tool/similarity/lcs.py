"""
Longest Common Subsequence (LCS) Module

Computes LCS-based similarity between two token lists.
Used by LexicalDetector.
"""

from typing import List

from my_tool.tokenizer import Token


def lcs_similarity(tokens_a: List[Token], tokens_b: List[Token]) -> float:
    """
    Compute the LCS-based similarity between two token lists.

    Uses dynamic programming to find the longest common subsequence
    (by token text), then returns the ratio relative to the smaller
    token list as a percentage.

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

    # Space-optimized LCS using single row
    curr = [0] * (n + 1)

    for i in range(1, m + 1):
        prev = 0
        for j in range(1, n + 1):
            backup = curr[j]
            if tokens_a[i - 1].value == tokens_b[j - 1].value:
                curr[j] = prev + 1
            else:
                curr[j] = max(curr[j], curr[j - 1])
            prev = backup

    lcs_length = curr[n]

    # Ratio relative to the smaller list
    smaller_size = min(m, n)
    if smaller_size == 0:
        return 0.0

    return (lcs_length / smaller_size) * 100.0
