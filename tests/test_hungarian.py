"""Tests for Hungarian algorithm module."""

import pytest
from my_tool.similarity.hungarian import find_assignments, create_bipartite_matrix


class TestHungarianAlgorithm:
    """Tests for the Hungarian Algorithm implementation."""

    def test_empty_matrix(self):
        with pytest.raises(ValueError):
            find_assignments([])

    def test_identity_matrix(self):
        """Optimal assignment for identity-like cost matrix."""
        costs = [
            [0, 10, 10],
            [10, 0, 10],
            [10, 10, 0],
        ]
        result = find_assignments(costs)
        assert result == [0, 1, 2]

    def test_simple_assignment(self):
        costs = [
            [1, 2, 3],
            [2, 4, 6],
            [3, 6, 9],
        ]
        result = find_assignments(costs)
        assert len(result) == 3
        # Each agent should be assigned to a different task
        assert len(set(result)) == 3

    def test_2x2_matrix(self):
        costs = [
            [1, 4],
            [3, 2],
        ]
        result = find_assignments(costs)
        assert len(result) == 2
        # Optimal: agent 0 → task 0 (cost 1), agent 1 → task 1 (cost 2) = total 3
        # or: agent 0 → task 1 (cost 4), agent 1 → task 0 (cost 3) = total 7
        total_cost = sum(costs[i][result[i]] for i in range(2))
        assert total_cost == 3

    def test_1x1_matrix(self):
        result = find_assignments([[5]])
        assert result == [0]

    def test_equal_costs(self):
        """All equal costs — any assignment is optimal."""
        costs = [
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
        ]
        result = find_assignments(costs)
        assert len(result) == 3
        assert len(set(result)) == 3  # unique assignments


class TestCreateBipartiteMatrix:
    """Tests for create_bipartite_matrix()."""

    def test_identical_features(self):
        features = [[1, 2, 3], [4, 5, 6]]
        result = create_bipartite_matrix(features, features)
        # Diagonal should be 0 (same row mapped to itself)
        assert result[0][0] == 0
        assert result[1][1] == 0

    def test_different_features(self):
        a = [[1, 0, 0]]
        b = [[0, 1, 0]]
        result = create_bipartite_matrix(a, b)
        assert result[0][0] > 0  # Different features → positive distance
