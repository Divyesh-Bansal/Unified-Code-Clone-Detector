"""
Euclidean Distance Module

Computes Euclidean distance between feature matrices.
Used by StructuralDetector.
"""

import math
from typing import List

from my_tool.similarity.feature_extractor import VariableFeatures


def euclidean_distance(features_a: List[List[int]],
                       features_b: List[List[int]]) -> float:
    """
    Compute the flat Euclidean distance between two feature matrices,
    assuming 1-to-1 row mapping.

    Args:
        features_a: Feature matrix for method A (list of feature vectors).
        features_b: Feature matrix for method B (list of feature vectors).

    Returns:
        Euclidean distance (>= 0).
    """
    if not features_a or not features_b:
        return float('inf')

    smaller_rows = min(len(features_a), len(features_b))
    sum_sq = 0.0

    for i in range(smaller_rows):
        cols = min(len(features_a[i]), len(features_b[i]))
        for j in range(cols):
            sum_sq += (features_a[i][j] - features_b[i][j]) ** 2

    return math.sqrt(sum_sq)


def euclidean_distance_mapped(features_a: List[List[int]],
                              features_b: List[List[int]],
                              mapping: List[int]) -> float:
    """
    Compute Euclidean distance with row mappings (from Hungarian algorithm).

    Args:
        features_a: Feature matrix for method A.
        features_b: Feature matrix for method B.
        mapping: Row mapping from A to B (mapping[i] = j means row i of A
                 maps to row j of B).

    Returns:
        Euclidean distance (>= 0).
    """
    if not features_a or not features_b or not mapping:
        return float('inf')

    smaller_rows = min(len(features_a), len(features_b), len(mapping))
    sum_sq = 0.0

    for i in range(smaller_rows):
        mapped_row = mapping[i]
        if mapped_row < 0 or mapped_row >= len(features_b):
            continue
        cols = min(len(features_a[i]), len(features_b[mapped_row]))
        for j in range(cols):
            sum_sq += (features_a[i][j] - features_b[mapped_row][j]) ** 2

    return math.sqrt(sum_sq)


def structural_similarity(vars_a: List[VariableFeatures],
                          vars_b: List[VariableFeatures]) -> float:
    """
    StructuralDetector similarity score.

    Pipeline:
      1. Build feature matrices from variable feature vectors
      2. Pad to equal size (zero-pad shorter matrix)
      3. Use Hungarian algorithm to find optimal variable-to-variable mapping
      4. Compute Euclidean distance WITH that optimal mapping
      5. Normalize by variable count if > 3 variables
      6. Convert to similarity percentage

    Combines feature distance and optimal variable mapping into a single score.

    Args:
        vars_a: Variable features for method A.
        vars_b: Variable features for method B.

    Returns:
        Similarity percentage (0-100).
    """
    from my_tool.similarity.hungarian import create_bipartite_matrix, find_assignments

    if not vars_a or not vars_b:
        return 0.0

    mat_a = [v.features for v in vars_a]
    mat_b = [v.features for v in vars_b]

    max_len = max(len(mat_a), len(mat_b))
    min_len = min(len(mat_a), len(mat_b))

    if min_len == 0:
        return 0.0

    # Heuristic: if variable counts differ too much, treat as different
    if max_len > 2 * min_len:
        return 0.0

    # Pad shorter matrix with zero rows to equal size
    feature_len = len(mat_a[0]) if mat_a else 0
    while len(mat_a) < max_len:
        mat_a.append([0] * feature_len)
    while len(mat_b) < max_len:
        mat_b.append([0] * feature_len)

    # Step 1: Build bipartite cost matrix and find optimal variable mapping
    cost_matrix = create_bipartite_matrix(mat_a, mat_b)
    try:
        mapping = find_assignments(cost_matrix)
    except (ValueError, IndexError):
        return 0.0

    # Step 2: Compute Euclidean distance WITH the optimal variable mapping
    dist = euclidean_distance_mapped(mat_a, mat_b, mapping)

    # Step 3: Normalize by variable count if above minimum
    if max_len > 3:
        dist /= max_len

    # Step 4: Convert distance to similarity percentage
    similarity = (1.0 / (1.0 + dist)) * 100.0
    return round(similarity, 2)
