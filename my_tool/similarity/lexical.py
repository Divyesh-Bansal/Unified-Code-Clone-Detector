"""
Lexical Detector Module

Combines Cosine Similarity and LCS with Token Weight to produce
the LexicalDetector combined score.

Formula: LexicalScore = ((Cosine + LCS) / 2) × TokenWeight
"""

from typing import Dict, List

from my_tool.tokenizer import Token
from my_tool.similarity.cosine import cosine_similarity
from my_tool.similarity.lcs import lcs_similarity
from my_tool.similarity.weight import naive_weight


def lexical_score(tokens_a: List[Token], tokens_b: List[Token]) -> Dict[str, float]:
    """
    Compute the LexicalDetector combined similarity score.

    Formula: ((cosine_score + lcs_score) / 2) × token_weight

    Args:
        tokens_a: First method's normalized token list.
        tokens_b: Second method's normalized token list.

    Returns:
        Dictionary with individual scores and combined lexical score:
        {
            'cosine': float,
            'lcs': float,
            'weight': float,
            'lexical': float
        }
    """
    if not tokens_a or not tokens_b:
        return {'cosine': 0.0, 'lcs': 0.0, 'weight': 0.0, 'lexical': 0.0}

    cos = cosine_similarity(tokens_a, tokens_b)
    lcs = lcs_similarity(tokens_a, tokens_b)
    weight = naive_weight(tokens_a, tokens_b)

    combined = ((cos + lcs) / 2.0) * weight

    return {
        'cosine': round(cos, 2),
        'lcs': round(lcs, 2),
        'weight': round(weight * 100, 2),
        'lexical': round(combined, 2)
    }
