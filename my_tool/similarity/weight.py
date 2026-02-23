"""
Token Weight Module

Computes a size-adjustment weight between two methods based on their
token count ratio. Used by LexicalDetector.
"""

from typing import List

from my_tool.tokenizer import Token


def naive_weight(tokens_a: List[Token], tokens_b: List[Token]) -> float:
    """
    Compute the naive weight (size ratio) between two token lists.

    Weight = smaller_size / larger_size

    This penalizes comparisons between methods of very different sizes.

    Args:
        tokens_a: First method's token list.
        tokens_b: Second method's token list.

    Returns:
        Weight as a decimal (0.0 to 1.0).
    """
    if not tokens_a or not tokens_b:
        return 0.0

    size_a = len(tokens_a)
    size_b = len(tokens_b)

    smaller = min(size_a, size_b)
    larger = max(size_a, size_b)

    if larger == 0:
        return 0.0

    return smaller / larger
