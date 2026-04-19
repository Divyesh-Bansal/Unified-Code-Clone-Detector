"""
Semantic Validation Module — Tiered Pipeline

Tier 1 (Fast-Pass):  Lightweight token/count heuristics (return type,
       parameter count, control-flow keywords, token-type distribution).
       If the combined score is below 30 % the pair is rejected early.

Tier 2 (Deep Analysis):  Builds a structural node sequence from the token
       stream (a pseudo-AST) and computes N-gram Jaccard similarity.
       Variable names and literals are ignored so logic clones with
       renamed identifiers are still detected.

Final score = 15 % return-type + 15 % param-count + 70 % AST-sequence.
"""

import math
from typing import Dict, List, Tuple

from my_tool.tokenizer import Token


# ── Tier-1 helpers (unchanged logic) ─────────────────────────────────────

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
        max_c = max(count_a, count_b)
        min_c = min(count_a, count_b)

        if max_c > 0:
            match_score += min_c / max_c
            total += 1.0

    if total == 0:
        return 100.0

    return (match_score / total) * 100.0


def _extract_control_flow(tokens: List[Token]) -> Dict[str, int]:
    """Extract control flow keyword counts."""
    cf_keywords = frozenset(['if', 'else', 'for', 'while', 'do', 'switch',
                              'case', 'break', 'continue', 'return', 'try',
                              'catch', 'throw', 'foreach'])
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


# ── Tier-1 aggregate ─────────────────────────────────────────────────────

_FAST_PASS_THRESHOLD = 30.0  # below this → skip Tier 2


def _tier1_score(tokens_a: List[Token], tokens_b: List[Token],
                 return_type_a: str, return_type_b: str,
                 param_count_a: int, param_count_b: int) -> Tuple[float, float, float, float, float]:
    """
    Compute all four lightweight heuristic scores and a combined average.

    Returns:
        (type_score, param_score, cf_score, dist_score, combined)
    """
    ts = _return_type_score(return_type_a, return_type_b)
    ps = _param_count_score(param_count_a, param_count_b)
    cf = _control_flow_score(tokens_a, tokens_b)
    ds = _type_distribution_score(tokens_a, tokens_b)
    combined = (ts + ps + cf + ds) / 4.0
    return ts, ps, cf, ds, combined


# ── Tier-2: Structural pseudo-AST ────────────────────────────────────────

# Control-flow keywords that are followed by '(' in all three languages
_CF_PAREN_KEYWORDS = frozenset(['if', 'for', 'while', 'switch', 'foreach'])

# Map keyword → structural node name (for keywords that stand alone)
_STANDALONE_KEYWORD_NODES: Dict[str, str] = {
    'do': 'DoWhileLoop',
    'else': 'ElseBranch',
    'return': 'ReturnStmt',
    'try': 'TryBlock',
    'catch': 'CatchBlock',
    'throw': 'ThrowStmt',
    'break': 'BreakStmt',
    'continue': 'ContinueStmt',
    'case': 'CaseClause',
    'default': 'DefaultClause',
    'finally': 'FinallyBlock',
}

# Map cf-paren keyword → structural node name
_CF_PAREN_NODES: Dict[str, str] = {
    'if': 'IfStmt',
    'for': 'ForLoop',
    'while': 'WhileLoop',
    'switch': 'SwitchStmt',
    'foreach': 'ForEachLoop',
}

# Binary operators to detect
_BINARY_OPS = frozenset(['+', '-', '*', '/', '%', '<', '>', '<=', '>=',
                          '==', '!=', '&&', '||', '&', '|', '^', '<<', '>>'])

# Assignment operators
_ASSIGN_OPS = frozenset(['=', '+=', '-=', '*=', '/=', '%=', '&=', '|=',
                          '^=', '<<=', '>>='])


def _tokens_to_structural_nodes(tokens: List[Token]) -> List[str]:
    """
    Walk the token stream and emit high-level structural node names.

    Variable names, literal values, and identifiers are ignored —
    only structural nodes are emitted.  This makes the sequence
    identical for logic clones that differ only in variable naming.
    """
    nodes: List[str] = []
    size = len(tokens)
    i = 0

    while i < size:
        tok = tokens[i]

        # ── Keywords ──────────────────────────────────────────────
        if tok.type == 'KEYWORD':
            # Control-flow keywords that expect '('
            if tok.value in _CF_PAREN_KEYWORDS:
                nodes.append(_CF_PAREN_NODES[tok.value])
                i += 1
                continue

            # Standalone keyword nodes
            if tok.value in _STANDALONE_KEYWORD_NODES:
                nodes.append(_STANDALONE_KEYWORD_NODES[tok.value])
                i += 1
                continue

        # ── Variable / type declarations ──────────────────────────
        if tok.type == 'DATATYPE':
            # A datatype at the beginning of a statement is likely a
            # variable declaration.  We look ahead to confirm.
            if i + 1 < size and tokens[i + 1].type == 'IDENTIFIER':
                nodes.append('VarDecl')
                i += 1
                continue

        # ── Function calls: IDENTIFIER '(' ────────────────────────
        if tok.type == 'IDENTIFIER' and i + 1 < size:
            if tokens[i + 1].type == 'LPAREN':
                nodes.append('CallExpr')
                i += 2  # skip past the '(' as well
                continue

        # ── Braces (block boundaries) ─────────────────────────────
        if tok.type == 'LBRACE':
            nodes.append('Block')
            i += 1
            continue

        if tok.type == 'RBRACE':
            nodes.append('EndBlock')
            i += 1
            continue

        # ── Operators ─────────────────────────────────────────────
        if tok.type == 'OPERATOR':
            if tok.value in _ASSIGN_OPS and tok.value != '=':
                # Compound assignment is both assignment and expression
                nodes.append('Assignment')
                i += 1
                continue
            if tok.value == '=':
                # Distinguish '=' (assignment) from '==' (comparison).
                # '==' is already handled as a binary op below.
                nodes.append('Assignment')
                i += 1
                continue
            if tok.value in _BINARY_OPS:
                nodes.append('BinaryExpr')
                i += 1
                continue

        # ── Statement terminator ──────────────────────────────────
        if tok.type == 'SEMICOLON':
            nodes.append('StmtEnd')
            i += 1
            continue

        # ── Everything else (identifiers, literals, etc.) skipped ─
        i += 1

    return nodes


# ── N-gram Jaccard ────────────────────────────────────────────────────────

def _extract_ngrams(seq: List[str], n: int) -> Dict[Tuple[str, ...], int]:
    """
    Extract n-gram *multiset* (with counts) from a sequence.

    Returns a dict mapping each n-gram tuple → its occurrence count.
    Using a multiset (counting duplicates) is more precise than a plain
    set for methods that repeat the same structural pattern.
    """
    counts: Dict[Tuple[str, ...], int] = {}
    for i in range(len(seq) - n + 1):
        gram = tuple(seq[i:i + n])
        counts[gram] = counts.get(gram, 0) + 1
    return counts


def _ngram_jaccard(seq_a: List[str], seq_b: List[str], n: int = 3) -> float:
    """
    Compute generalised Jaccard similarity over n-gram multisets.

    For multisets A and B the generalised Jaccard index is:
        J(A,B) = Σ min(A[g], B[g]) / Σ max(A[g], B[g])

    Returns a percentage (0-100).
    """
    grams_a = _extract_ngrams(seq_a, n)
    grams_b = _extract_ngrams(seq_b, n)

    if not grams_a and not grams_b:
        return 100.0  # both empty → identical
    if not grams_a or not grams_b:
        return 0.0

    all_grams = set(grams_a.keys()) | set(grams_b.keys())

    intersection = 0
    union = 0
    for g in all_grams:
        ca = grams_a.get(g, 0)
        cb = grams_b.get(g, 0)
        intersection += min(ca, cb)
        union += max(ca, cb)

    if union == 0:
        return 0.0

    return (intersection / union) * 100.0


def _ast_sequence_score(tokens_a: List[Token],
                        tokens_b: List[Token]) -> float:
    """
    Deep structural comparison using N-gram Jaccard on pseudo-AST
    node sequences extracted from the token streams.

    Uses n=3 by default; falls back to n=2 (then n=1) for very
    short methods where n=3 would produce too few n-grams.
    """
    nodes_a = _tokens_to_structural_nodes(tokens_a)
    nodes_b = _tokens_to_structural_nodes(tokens_b)

    # Pick the largest n that yields at least 2 n-grams from both sides
    min_len = min(len(nodes_a), len(nodes_b))

    if min_len == 0:
        # No structural nodes at all — fall back to 0
        return 0.0

    for n in (3, 2, 1):
        if min_len >= n + 1:  # at least 2 n-grams
            return _ngram_jaccard(nodes_a, nodes_b, n)

    # Sequences are extremely short — direct comparison
    if nodes_a == nodes_b:
        return 100.0
    return 0.0


# ── Public API ────────────────────────────────────────────────────────────

def semantic_similarity(tokens_a: List[Token], tokens_b: List[Token],
                        return_type_a: str = "", return_type_b: str = "",
                        param_count_a: int = 0, param_count_b: int = 0) -> float:
    """
    Compute semantic similarity between two methods using a tiered pipeline.

    Tier 1: Fast token/count heuristics.  If the combined score is
            below 30 % the pair is rejected immediately.
    Tier 2: Structural pseudo-AST N-gram Jaccard similarity.

    Final score = 15 % return-type + 15 % param-count + 70 % AST-sequence.

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

    # ── Tier 1: fast-pass filter ──────────────────────────────────
    ts, ps, cf, ds, combined = _tier1_score(
        tokens_a, tokens_b,
        return_type_a, return_type_b,
        param_count_a, param_count_b,
    )

    if combined < _FAST_PASS_THRESHOLD:
        # Not similar enough to justify deep analysis — return the
        # lightweight estimate directly.
        return round(combined, 2)

    # ── Tier 2: deep AST-sequence analysis ────────────────────────
    ast_score = _ast_sequence_score(tokens_a, tokens_b)

    # Final combination: contextual metadata + structural score
    final = (ts * 0.15) + (ps * 0.15) + (ast_score * 0.70)

    return round(final, 2)
