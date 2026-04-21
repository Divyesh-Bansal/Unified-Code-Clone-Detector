"""
File-Level Similarity Module

Implements the "Hybrid Ensemble" detection for file-level comparison:

  * Lexical  (holistic):   Full file tokens → lexical_score()
  * Structural (bipartite): Greedy best-match over all function pairs
  * Semantic   (bipartite): Greedy best-match over all function pairs

Final score uses the same weights as function-level mode.
"""

from typing import List

from my_tool.tokenizer import Token
from my_tool.method_extractor import MethodInfo
from my_tool.normalizer import normalize
from my_tool.similarity.lexical import lexical_score
from my_tool.similarity.feature_extractor import extract_features
from my_tool.similarity.euclidean import structural_similarity
from my_tool.similarity.semantic import semantic_similarity
from my_tool.similarity.hybrid import (
    SimilarityResult,
    WEIGHT_LEXICAL,
    WEIGHT_STRUCTURAL,
    WEIGHT_SEMANTIC,
    classify_confidence,
)


def _bipartite_best_match_score(
    methods_a: List[MethodInfo],
    methods_b: List[MethodInfo],
    scorer,
) -> float:
    """
    Greedy bipartite best-match scoring.

    For each function in the *smaller* list, find the highest-scoring
    partner in the larger list, then average the best-match scores.

    Args:
        methods_a: Functions extracted from file A.
        methods_b: Functions extracted from file B.
        scorer:    Callable(method_a, method_b) → float (0-100).

    Returns:
        Average best-match score (0-100), or 0.0 if either list is empty.
    """
    if not methods_a or not methods_b:
        return 0.0

    # Always iterate over the smaller side for efficiency
    if len(methods_a) > len(methods_b):
        methods_a, methods_b = methods_b, methods_a

    best_scores: List[float] = []
    for m_a in methods_a:
        best = max(scorer(m_a, m_b) for m_b in methods_b)
        best_scores.append(best)

    return sum(best_scores) / len(best_scores)


def _structural_scorer(m_a: MethodInfo, m_b: MethodInfo) -> float:
    """Compute structural similarity between two methods."""
    vars_a = extract_features(m_a.tokens)
    vars_b = extract_features(m_b.tokens)
    return structural_similarity(vars_a, vars_b)


def _semantic_scorer(m_a: MethodInfo, m_b: MethodInfo) -> float:
    """Compute semantic similarity between two methods."""
    return semantic_similarity(
        m_a.tokens, m_b.tokens,
        m_a.return_type, m_b.return_type,
        m_a.param_count, m_b.param_count,
    )


def compute_file_similarity(
    tokens_a: List[Token],
    tokens_b: List[Token],
    methods_a: List[MethodInfo],
    methods_b: List[MethodInfo],
) -> SimilarityResult:
    """
    Compute hybrid similarity between two entire source files.

    Lexical scoring is holistic (full file tokens).
    Structural and semantic scoring use bipartite best-match
    over extracted functions.

    Args:
        tokens_a:  All tokens from file A (full file).
        tokens_b:  All tokens from file B (full file).
        methods_a: Functions extracted from file A.
        methods_b: Functions extracted from file B.

    Returns:
        SimilarityResult with all scores and confidence level.
    """
    if not tokens_a or not tokens_b:
        return SimilarityResult(
            lexical_score=0.0, structural_score=0.0, semantic_score=0.0,
            hybrid_score=0.0, confidence="LOW", details={},
        )

    # ── 1. Lexical: holistic over the whole file ──────────────────
    norm_a, _ = normalize(tokens_a)
    norm_b, _ = normalize(tokens_b)
    lex = lexical_score(norm_a, norm_b)
    lex_val = lex['lexical']

    # ── 2. Structural: bipartite best-match ───────────────────────
    struct_val = _bipartite_best_match_score(
        methods_a, methods_b, _structural_scorer,
    )

    # ── 3. Semantic: bipartite best-match ─────────────────────────
    sem_val = _bipartite_best_match_score(
        methods_a, methods_b, _semantic_scorer,
    )

    # ── 4. Weighted ensemble (same weights as function mode) ──────
    hybrid = (lex_val * WEIGHT_LEXICAL +
              struct_val * WEIGHT_STRUCTURAL +
              sem_val * WEIGHT_SEMANTIC)
    hybrid = round(hybrid, 2)
    confidence = classify_confidence(hybrid)

    details = {
        'lexical_details': lex,
        'structural_details': {
            'methods_a_count': len(methods_a),
            'methods_b_count': len(methods_b),
            'matching_strategy': 'bipartite_best_match',
        },
        'weights': {
            'lexical': WEIGHT_LEXICAL,
            'structural': WEIGHT_STRUCTURAL,
            'semantic': WEIGHT_SEMANTIC,
        },
    }

    return SimilarityResult(
        lexical_score=lex_val,
        structural_score=struct_val,
        semantic_score=sem_val,
        hybrid_score=hybrid,
        confidence=confidence,
        details=details,
    )
