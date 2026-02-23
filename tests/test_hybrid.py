"""Tests for hybrid similarity module."""

import pytest
from my_tool.tokenizer import tokenize
from my_tool.similarity.hybrid import (
    compute_hybrid_similarity,
    classify_confidence,
    SimilarityResult,
)


class TestClassifyConfidence:
    """Tests for classify_confidence()."""

    def test_very_high(self):
        assert classify_confidence(95.0) == "VERY HIGH"

    def test_high(self):
        assert classify_confidence(80.0) == "HIGH"

    def test_medium(self):
        assert classify_confidence(65.0) == "MEDIUM"

    def test_low(self):
        assert classify_confidence(40.0) == "LOW"

    def test_boundary_90(self):
        assert classify_confidence(90.0) == "HIGH"  # 90.0 is not > 90
        assert classify_confidence(90.1) == "VERY HIGH"

    def test_boundary_75(self):
        assert classify_confidence(75.0) == "MEDIUM"  # 75.0 is not > 75
        assert classify_confidence(75.1) == "HIGH"

    def test_boundary_60(self):
        assert classify_confidence(60.0) == "LOW"  # 60.0 is not > 60
        assert classify_confidence(60.1) == "MEDIUM"


class TestComputeHybridSimilarity:
    """Tests for compute_hybrid_similarity()."""

    def test_empty_inputs(self):
        result = compute_hybrid_similarity([], [])
        assert result.hybrid_score == 0.0
        assert result.confidence == "LOW"

    def test_identical_code(self):
        code = "int add(int a, int b) { return a + b; }"
        tokens = tokenize(code)
        result = compute_hybrid_similarity(tokens, tokens, "int", "int", 2, 2)
        assert result.hybrid_score > 50.0
        assert isinstance(result, SimilarityResult)

    def test_result_structure(self):
        code = "int x = 5;"
        tokens = tokenize(code)
        result = compute_hybrid_similarity(tokens, tokens)
        assert hasattr(result, 'lexical_score')
        assert hasattr(result, 'structural_score')
        assert hasattr(result, 'semantic_score')
        assert hasattr(result, 'hybrid_score')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'details')

    def test_renamed_vars_high_score(self):
        """Renamed variables should still produce high similarity."""
        code_a = """
        int findMax(int arr[], int n) {
            int maxVal = arr[0];
            for (int i = 1; i < n; i++) {
                if (arr[i] > maxVal) {
                    maxVal = arr[i];
                }
            }
            return maxVal;
        }
        """
        code_b = """
        int getLargest(int data[], int count) {
            int biggest = data[0];
            for (int j = 1; j < count; j++) {
                if (data[j] > biggest) {
                    biggest = data[j];
                }
            }
            return biggest;
        }
        """
        tokens_a = tokenize(code_a)
        tokens_b = tokenize(code_b)
        result = compute_hybrid_similarity(tokens_a, tokens_b, "int", "int", 2, 2)
        assert result.hybrid_score > 40.0

    def test_different_code_lower_score(self):
        """Very different code should score lower."""
        code_a = "int add(int a, int b) { return a + b; }"
        code_b = """
        void bubbleSort(int arr[], int n) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (arr[j] > arr[j+1]) {
                        int t = arr[j];
                        arr[j] = arr[j+1];
                        arr[j+1] = t;
                    }
                }
            }
        }
        """
        tokens_a = tokenize(code_a)
        tokens_b = tokenize(code_b)
        result = compute_hybrid_similarity(tokens_a, tokens_b, "int", "void", 2, 2)
        assert result.hybrid_score < 60.0

    def test_scores_bounded(self):
        """All scores should be between 0 and 100."""
        code = "int f(int x) { return x * 2; }"
        tokens = tokenize(code)
        result = compute_hybrid_similarity(tokens, tokens)
        assert 0 <= result.lexical_score <= 100
        assert 0 <= result.structural_score <= 100
        assert 0 <= result.semantic_score <= 100
        assert 0 <= result.hybrid_score <= 100
