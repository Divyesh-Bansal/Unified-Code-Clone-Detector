"""
Hungarian Algorithm Module

Full implementation of the Hungarian (Munkres) Algorithm for optimal
bipartite matching. Used by StructuralDetector to find the optimal
variable-to-variable mapping between two methods that minimizes total
Euclidean distance.
"""

import math
from typing import List, Optional, Tuple

from my_tool.similarity.feature_extractor import VariableFeatures


def find_assignments(cost_matrix: List[List[int]]) -> List[int]:
    """
    Find optimal assignments using the Hungarian Algorithm.

    Finds the assignment of rows to columns that minimizes total cost.

    Args:
        cost_matrix: 2D cost matrix where cost_matrix[i][j] is the cost
                     of assigning row i to column j. Must be square.

    Returns:
        List where result[i] is the column assigned to row i.

    Raises:
        ValueError: If cost_matrix is empty or not square.
    """
    if not cost_matrix or not cost_matrix[0]:
        raise ValueError("Cost matrix cannot be empty")

    h = len(cost_matrix)
    w = len(cost_matrix[0])

    # Work on a copy
    costs = [row[:] for row in cost_matrix]

    # Step 0: Subtract row minimums
    for i in range(h):
        min_val = min(costs[i])
        for j in range(w):
            costs[i][j] -= min_val

    masks = [[0] * w for _ in range(h)]
    rows_covered = [False] * h
    cols_covered = [False] * w

    # Initial starring of zeros
    for i in range(h):
        for j in range(w):
            if costs[i][j] == 0 and not rows_covered[i] and not cols_covered[j]:
                masks[i][j] = 1
                rows_covered[i] = True
                cols_covered[j] = True

    _clear_covers(rows_covered, cols_covered)

    path = [(0, 0)] * (w * h)
    path_start = (0, 0)
    step = 1

    while step != -1:
        if step == 1:
            step = _step1(masks, cols_covered, w, h)
        elif step == 2:
            step, path_start = _step2(costs, masks, rows_covered, cols_covered, w, h)
        elif step == 3:
            step = _step3(masks, rows_covered, cols_covered, w, h, path, path_start)
        elif step == 4:
            step = _step4(costs, rows_covered, cols_covered, w, h)

    # Extract assignments
    result = [0] * h
    for i in range(h):
        for j in range(w):
            if masks[i][j] == 1:
                result[i] = j
                break

    return result


def _step1(masks, cols_covered, w, h):
    """Cover columns containing starred zeros."""
    for i in range(h):
        for j in range(w):
            if masks[i][j] == 1:
                cols_covered[j] = True

    count = sum(1 for j in range(w) if cols_covered[j])
    return -1 if count >= h else 2


def _step2(costs, masks, rows_covered, cols_covered, w, h):
    """Find uncovered zeros and star/prime them."""
    path_start = (0, 0)

    while True:
        loc = _find_zero(costs, rows_covered, cols_covered, w, h)
        if loc[0] == -1:
            return 4, path_start

        masks[loc[0]][loc[1]] = 2
        star_col = _find_star_in_row(masks, w, loc[0])

        if star_col != -1:
            rows_covered[loc[0]] = True
            cols_covered[star_col] = False
        else:
            path_start = loc
            return 3, path_start


def _step3(masks, rows_covered, cols_covered, w, h, path, path_start):
    """Augment the path of starred/primed zeros."""
    path_index = 0
    path[0] = path_start

    while True:
        row = _find_star_in_column(masks, h, path[path_index][1])
        if row == -1:
            break

        path_index += 1
        path[path_index] = (row, path[path_index - 1][1])

        col = _find_prime_in_row(masks, w, path[path_index][0])

        path_index += 1
        path[path_index] = (path[path_index - 1][0], col)

    _convert_path(masks, path, path_index + 1)
    _clear_covers(rows_covered, cols_covered)
    _clear_primes(masks, w, h)

    return 1


def _step4(costs, rows_covered, cols_covered, w, h):
    """Add and subtract minimum uncovered value."""
    min_val = _find_minimum(costs, rows_covered, cols_covered, w, h)

    for i in range(h):
        for j in range(w):
            if rows_covered[i]:
                costs[i][j] += min_val
            if not cols_covered[j]:
                costs[i][j] -= min_val

    return 2


def _find_zero(costs, rows_covered, cols_covered, w, h):
    for i in range(h):
        for j in range(w):
            if costs[i][j] == 0 and not rows_covered[i] and not cols_covered[j]:
                return (i, j)
    return (-1, -1)


def _find_minimum(costs, rows_covered, cols_covered, w, h):
    min_val = float('inf')
    for i in range(h):
        for j in range(w):
            if not rows_covered[i] and not cols_covered[j]:
                min_val = min(min_val, costs[i][j])
    return min_val if min_val != float('inf') else 0


def _find_star_in_row(masks, w, row):
    for j in range(w):
        if masks[row][j] == 1:
            return j
    return -1


def _find_star_in_column(masks, h, col):
    for i in range(h):
        if masks[i][col] == 1:
            return i
    return -1


def _find_prime_in_row(masks, w, row):
    for j in range(w):
        if masks[row][j] == 2:
            return j
    return -1


def _convert_path(masks, path, path_length):
    for i in range(path_length):
        r, c = path[i]
        if masks[r][c] == 1:
            masks[r][c] = 0
        elif masks[r][c] == 2:
            masks[r][c] = 1


def _clear_covers(rows_covered, cols_covered):
    for i in range(len(rows_covered)):
        rows_covered[i] = False
    for j in range(len(cols_covered)):
        cols_covered[j] = False


def _clear_primes(masks, w, h):
    for i in range(h):
        for j in range(w):
            if masks[i][j] == 2:
                masks[i][j] = 0


def create_bipartite_matrix(features_a: List[List[int]],
                            features_b: List[List[int]]) -> List[List[int]]:
    """
    Create a bipartite cost matrix from two variable feature matrices.

    Each entry [i][j] is the Euclidean distance between variable i from
    method A and variable j from method B, cast to int (matching
    BiPartite.CreateBipartiteMatrix()).

    Args:
        features_a: Feature matrix for method A.
        features_b: Feature matrix for method B.

    Returns:
        Square cost matrix for the Hungarian Algorithm.
    """
    n = len(features_a)
    m = len(features_b)
    size = max(n, m)

    # Pad to make square
    feat_len = len(features_a[0]) if features_a and features_a[0] else 0

    padded_a = [row[:] for row in features_a]
    while len(padded_a) < size:
        padded_a.append([0] * feat_len)

    padded_b = [row[:] for row in features_b]
    while len(padded_b) < size:
        padded_b.append([0] * feat_len)

    adjacent = [[0] * size for _ in range(size)]

    for i in range(size):
        for j in range(size):
            temp = 0.0
            cols = min(len(padded_a[i]), len(padded_b[j]))
            for k in range(cols):
                temp += (padded_a[i][k] - padded_b[j][k]) ** 2
            adjacent[i][j] = int(math.sqrt(temp))

    return adjacent


