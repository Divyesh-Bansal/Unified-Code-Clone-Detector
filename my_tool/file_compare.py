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
    items_a: list,
    items_b: list,
    scorer,
) -> float:
    """
    Greedy bipartite best-match scoring.

    For each function in the *smaller* list, find the highest-scoring
    partner in the larger list, then average the best-match scores.

    Args:
        items_a: Pairs of (MethodInfo, feature_dict) from file A.
        items_b: Pairs of (MethodInfo, feature_dict) from file B.
        scorer:  Callable(item_a, item_b) → float (0-100).

    Returns:
        Average best-match score (0-100), or 0.0 if either list is empty.
    """
    if not items_a or not items_b:
        return 0.0

    # Always iterate over the smaller side for efficiency
    if len(items_a) > len(items_b):
        items_a, items_b = items_b, items_a

    best_scores: List[float] = []
    for i_a in items_a:
        best = max(scorer(i_a, i_b) for i_b in items_b)
        best_scores.append(best)

    return sum(best_scores) / len(best_scores)


def _structural_scorer(item_a, item_b) -> float:
    """Compute structural similarity between two paired items."""
    _, vars_a = item_a
    _, vars_b = item_b
    return structural_similarity(vars_a, vars_b)


def _semantic_scorer(item_a, item_b) -> float:
    """Compute semantic similarity between two paired items."""
    m_a, _ = item_a
    m_b, _ = item_b
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
    norm_a: List[Token] = None,
    norm_b: List[Token] = None,
    features_a: list = None,
    features_b: list = None,
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
    if norm_a is None:
        norm_a, _ = normalize(tokens_a)
    if norm_b is None:
        norm_b, _ = normalize(tokens_b)
    lex = lexical_score(norm_a, norm_b)
    lex_val = lex['lexical']

    # ── 2. Structural: bipartite best-match ───────────────────────
    if features_a is None:
        features_a = [extract_features(m.tokens) for m in methods_a]
    if features_b is None:
        features_b = [extract_features(m.tokens) for m in methods_b]

    items_a = list(zip(methods_a, features_a))
    items_b = list(zip(methods_b, features_b))

    struct_val = _bipartite_best_match_score(
        items_a, items_b, _structural_scorer,
    )

    # ── 3. Semantic: bipartite best-match ─────────────────────────
    sem_val = _bipartite_best_match_score(
        items_a, items_b, _semantic_scorer,
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
