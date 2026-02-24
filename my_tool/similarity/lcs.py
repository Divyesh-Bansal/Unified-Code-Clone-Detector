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

    Uses a standard two-row dynamic programming algorithm to find the
    Longest Common Subsequence (matched by token text value).  The LCS
    length is then expressed as a percentage of the smaller list length.

    Two-row DP guarantees O(min(m,n)) space and O(m*n) time while being
    straightforward to verify: `prev_row` always holds the completed DP
    values for row i-1, and `curr_row` is filled left-to-right for row i
    with no aliasing issues.

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

    # Keep the shorter sequence as the column axis to minimise memory
    if m < n:
        tokens_a, tokens_b = tokens_b, tokens_a
        m, n = n, m

    # prev_row[j] = LCS length for tokens_a[:i-1] vs tokens_b[:j]
    prev_row = [0] * (n + 1)

    for i in range(1, m + 1):
        curr_row = [0] * (n + 1)
        for j in range(1, n + 1):
            if tokens_a[i - 1].value == tokens_b[j - 1].value:
                curr_row[j] = prev_row[j - 1] + 1          # diagonal + 1
            else:
                curr_row[j] = max(prev_row[j], curr_row[j - 1])  # skip left or up
        prev_row = curr_row

    lcs_length = prev_row[n]

    # Similarity relative to the shorter list (tokens_b after possible swap)
    smaller_size = n
    if smaller_size == 0:
        return 0.0

    return (lcs_length / smaller_size) * 100.0
