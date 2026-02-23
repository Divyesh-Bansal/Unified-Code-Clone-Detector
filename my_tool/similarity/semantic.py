"""
Semantic Validation Module

Performs structural and semantic comparison between two methods,
checking return types, parameter counts, control flow patterns,
and token structure compatibility.
"""

from typing import Dict, List

from my_tool.tokenizer import Token


def semantic_similarity(tokens_a: List[Token], tokens_b: List[Token],
                        return_type_a: str = "", return_type_b: str = "",
                        param_count_a: int = 0, param_count_b: int = 0) -> float:
    """
    Compute semantic similarity between two methods.

    Evaluates:
    1. Return type compatibility (25%)
    2. Parameter count similarity (25%)
    3. Control flow pattern similarity (25%)
    4. Token type distribution similarity (25%)

    Args:
        tokens_a: First method's token list.
        tokens_b: Second method's token list.
        return_type_a: Return type of method A.
        return_type_b: Return type of method B.
        param_count_a: Number of parameters for method A.
        param_count_b: Number of parameters for method B.

    Returns:
        Similarity percentage (0-100).
    """
    if not tokens_a or not tokens_b:
        return 0.0

    # 1. Return type compatibility (25%)
    type_score = _return_type_score(return_type_a, return_type_b)

    # 2. Parameter count similarity (25%)
    param_score = _param_count_score(param_count_a, param_count_b)

    # 3. Control flow pattern similarity (25%)
    cf_score = _control_flow_score(tokens_a, tokens_b)

    # 4. Token type distribution similarity (25%)
    dist_score = _type_distribution_score(tokens_a, tokens_b)

    # Weighted combination
    total = (type_score * 0.25 + param_score * 0.25 +
             cf_score * 0.25 + dist_score * 0.25)

    return round(total, 2)


# Type compatibility groups
_NUMERIC_TYPES = frozenset(['int', 'float', 'double', 'long', 'short',
                            'unsigned', 'signed', 'char', 'wchar_t'])
_CONTAINER_TYPES = frozenset(['vector', 'list', 'deque', 'array', 'set', 'map'])
_POINTER_TYPES = frozenset(['auto', 'void'])


def _return_type_score(type_a: str, type_b: str) -> float:
    """Score return type compatibility (0-100)."""
    if not type_a or not type_b:
        return 50.0  # Unknown types — neutral score

    if type_a == type_b:
        return 100.0

    # Same category = compatible
    for group in (_NUMERIC_TYPES, _CONTAINER_TYPES, _POINTER_TYPES):
        if type_a in group and type_b in group:
            return 85.0

    # Both are identifiers (custom types) — could be compatible
    if type_a[0].isupper() and type_b[0].isupper():
        return 60.0

    return 30.0


def _param_count_score(count_a: int, count_b: int) -> float:
    """Score parameter count similarity (0-100)."""
    if count_a == count_b:
        return 100.0

    diff = abs(count_a - count_b)
    max_count = max(count_a, count_b, 1)

    # Score decreases with difference
    score = max(0.0, 100.0 * (1.0 - diff / max_count))
    return score


def _control_flow_score(tokens_a: List[Token], tokens_b: List[Token]) -> float:
    """Compare control flow patterns between two methods."""
    cf_a = _extract_control_flow(tokens_a)
    cf_b = _extract_control_flow(tokens_b)

    if not cf_a and not cf_b:
        return 100.0  # Both have no control flow

    if not cf_a or not cf_b:
        return 20.0  # One has control flow, other doesn't

    # Compare counts of each control flow element
    all_keys = set(cf_a.keys()) | set(cf_b.keys())
    match_score = 0.0
    total = 0.0

    for key in all_keys:
        count_a = cf_a.get(key, 0)
        count_b = cf_b.get(key, 0)
        max_count = max(count_a, count_b)
        min_count = min(count_a, count_b)

        if max_count > 0:
            match_score += min_count / max_count
            total += 1.0

    if total == 0:
        return 100.0

    return (match_score / total) * 100.0


def _extract_control_flow(tokens: List[Token]) -> Dict[str, int]:
    """Extract control flow keyword counts."""
    cf_keywords = frozenset(['if', 'else', 'for', 'while', 'do', 'switch',
                              'case', 'break', 'continue', 'return', 'try',
                              'catch', 'throw'])
    counts: Dict[str, int] = {}
    for tok in tokens:
        if tok.type == 'KEYWORD' and tok.value in cf_keywords:
            counts[tok.value] = counts.get(tok.value, 0) + 1
    return counts


def _type_distribution_score(tokens_a: List[Token],
                             tokens_b: List[Token]) -> float:
    """Compare token type distributions between two methods."""
    dist_a = _token_type_distribution(tokens_a)
    dist_b = _token_type_distribution(tokens_b)

    all_types = set(dist_a.keys()) | set(dist_b.keys())

    if not all_types:
        return 100.0

    # Cosine similarity of type distributions
    dot = 0.0
    mag_a = 0.0
    mag_b = 0.0

    for t in all_types:
        va = dist_a.get(t, 0.0)
        vb = dist_b.get(t, 0.0)
        dot += va * vb
        mag_a += va * va
        mag_b += vb * vb

    import math
    denom = math.sqrt(mag_a) * math.sqrt(mag_b)
    if denom == 0:
        return 0.0

    return (dot / denom) * 100.0


def _token_type_distribution(tokens: List[Token]) -> Dict[str, float]:
    """Get normalized token type frequency distribution."""
    dist: Dict[str, float] = {}
    total = len(tokens)
    if total == 0:
        return dist

    for tok in tokens:
        dist[tok.type] = dist.get(tok.type, 0.0) + 1.0

    # Normalize
    for k in dist:
        dist[k] /= total

    return dist
