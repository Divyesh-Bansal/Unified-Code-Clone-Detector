"""
Hybrid Similarity Module

Combines all detectors into a weighted ensemble score
with confidence classification.

Final Score = (LexicalDetector × 0.50) + (StructuralDetector × 0.35) + (SemanticDetector × 0.15)
"""

from typing import Dict, List, NamedTuple, Optional

from my_tool.tokenizer import Token
from my_tool.normalizer import normalize
from my_tool.similarity.lexical import lexical_score
from my_tool.similarity.feature_extractor import extract_features
from my_tool.similarity.euclidean import structural_similarity
from my_tool.similarity.semantic import semantic_similarity


class SimilarityResult(NamedTuple):
    """Complete similarity analysis result for a method pair."""
    lexical_score: float    # LexicalDetector score (0-100)   — weight 50%
    structural_score: float # StructuralDetector score (0-100) — weight 35%
    semantic_score: float   # SemanticDetector score (0-100)  — weight 15%
    hybrid_score: float     # Final weighted score (0-100)
    confidence: str         # Confidence level (VERY HIGH, HIGH, MEDIUM, LOW)
    details: Dict           # Detailed sub-scores


# Weights for the ensemble
WEIGHT_LEXICAL = 0.45
WEIGHT_STRUCTURAL = 0.30
WEIGHT_SEMANTIC = 0.25


def classify_confidence(score: float) -> str:
    """
    Classify the confidence level based on the hybrid score.

    Args:
        score: Hybrid similarity score (0-100).

    Returns:
        Confidence level string.
    """
    if score > 90:
        return "VERY HIGH"
    elif score > 75:
        return "HIGH"
    elif score > 60:
        return "MEDIUM"
    else:
        return "LOW"


def compute_hybrid_similarity(tokens_a: List[Token], tokens_b: List[Token],
                              return_type_a: str = "",
                              return_type_b: str = "",
                              param_count_a: int = 0,
                              param_count_b: int = 0,
                              norm_a: Optional[List[Token]] = None,
                              norm_b: Optional[List[Token]] = None) -> SimilarityResult:
    """
    Compute the full hybrid similarity score between two methods.

    Runs LexicalDetector, StructuralDetector, and SemanticDetector, then
    produces a weighted ensemble score:
      50% LexicalDetector  +  35% StructuralDetector  +  15% SemanticDetector

    Args:
        tokens_a: Token list for method A (pre-extraction, original tokens).
        tokens_b: Token list for method B (pre-extraction, original tokens).
        return_type_a: Return type of method A.
        return_type_b: Return type of method B.
        param_count_a: Parameter count for method A.
        param_count_b: Parameter count for method B.

    Returns:
        SimilarityResult with all scores and confidence level.
    """
    if not tokens_a or not tokens_b:
        return SimilarityResult(
            lexical_score=0.0, structural_score=0.0, semantic_score=0.0,
            hybrid_score=0.0, confidence="LOW",
            details={}
        )

    # 1. Normalize tokens for LexicalDetector (use pre-computed versions if supplied)
    if norm_a is None:
        norm_a, _ = normalize(tokens_a)
    if norm_b is None:
        norm_b, _ = normalize(tokens_b)

    # 2. LexicalDetector: Cosine + LCS weighted by token size ratio
    lex = lexical_score(norm_a, norm_b)
    lex_val = lex['lexical']

    # 3. StructuralDetector: feature extraction → Hungarian mapping → mapped Euclidean
    vars_a = extract_features(tokens_a)
    vars_b = extract_features(tokens_b)
    struct_val = structural_similarity(vars_a, vars_b)

    # 4. SemanticDetector: return types, param counts, control flow, token distributions
    sem_val = semantic_similarity(
        tokens_a, tokens_b,
        return_type_a, return_type_b,
        param_count_a, param_count_b
    )

    # 5. Weighted ensemble
    hybrid = (lex_val * WEIGHT_LEXICAL +
              struct_val * WEIGHT_STRUCTURAL +
              sem_val * WEIGHT_SEMANTIC)

    hybrid = round(hybrid, 2)
    confidence = classify_confidence(hybrid)

    details = {
        'lexical_details': lex,
        'structural_details': {
            'vars_a_count': len(vars_a),
            'vars_b_count': len(vars_b),
        },
        'weights': {
            'lexical': WEIGHT_LEXICAL,
            'structural': WEIGHT_STRUCTURAL,
            'semantic': WEIGHT_SEMANTIC,
        }
    }

    return SimilarityResult(
        lexical_score=lex_val,
        structural_score=struct_val,
        semantic_score=sem_val,
        hybrid_score=hybrid,
        confidence=confidence,
        details=details
    )
