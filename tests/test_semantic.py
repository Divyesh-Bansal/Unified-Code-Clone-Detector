"""Tests for semantic similarity module."""

import pytest
from my_tool.tokenizer import tokenize
from my_tool.similarity.semantic import semantic_similarity


class TestSemanticSimilarity:
    """Tests for semantic_similarity()."""

    def test_empty_inputs(self):
        assert semantic_similarity([], []) == 0.0

    def test_identical_code(self):
        code = "int add(int a, int b) { return a + b; }"
        tokens = tokenize(code)
        score = semantic_similarity(tokens, tokens, "int", "int", 2, 2)
        assert score > 80.0

    def test_same_return_type_boost(self):
        code_a = "int f(int x) { return x + 1; }"
        code_b = "int g(int y) { return y + 2; }"
        tokens_a = tokenize(code_a)
        tokens_b = tokenize(code_b)
        score = semantic_similarity(tokens_a, tokens_b, "int", "int", 1, 1)
        assert score > 60.0

    def test_different_return_type(self):
        code_a = "int f(int x) { return x; }"
        code_b = "void g(int y) { cout << y; }"
        tokens_a = tokenize(code_a)
        tokens_b = tokenize(code_b)
        score_same = semantic_similarity(tokens_a, tokens_b, "int", "int", 1, 1)
        score_diff = semantic_similarity(tokens_a, tokens_b, "int", "void", 1, 1)
        # Same return type should score higher
        assert score_same >= score_diff

    def test_param_count_similarity(self):
        tokens = tokenize("int f(int a) { return a; }")
        score_same = semantic_similarity(tokens, tokens, "int", "int", 1, 1)
        score_diff = semantic_similarity(tokens, tokens, "int", "int", 1, 5)
        assert score_same >= score_diff

    def test_control_flow_match(self):
        code_a = """
        void f(int n) {
            for (int i = 0; i < n; i++) {
                if (i > 5) break;
            }
        }
        """
        code_b = """
        void g(int m) {
            for (int j = 0; j < m; j++) {
                if (j > 5) break;
            }
        }
        """
        tokens_a = tokenize(code_a)
        tokens_b = tokenize(code_b)
        score = semantic_similarity(tokens_a, tokens_b, "void", "void", 1, 1)
        assert score > 70.0
