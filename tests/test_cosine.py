"""Tests for cosine similarity module."""

import pytest
from my_tool.tokenizer import tokenize
from my_tool.normalizer import normalize
from my_tool.similarity.cosine import cosine_similarity


class TestCosineSimilarity:
    """Tests for cosine_similarity()."""

    def test_empty_inputs(self):
        assert cosine_similarity([], []) == 0.0

    def test_one_empty(self):
        tokens = tokenize("int x = 5;")
        assert cosine_similarity(tokens, []) == 0.0
        assert cosine_similarity([], tokens) == 0.0

    def test_identical_tokens(self):
        tokens = tokenize("int x = 5;")
        score = cosine_similarity(tokens, tokens)
        assert score == pytest.approx(100.0, abs=0.1)

    def test_similar_tokens(self):
        """Similar code should have high cosine similarity."""
        code_a = "int x = 5; int y = 10;"
        code_b = "int a = 5; int b = 10;"
        tokens_a, _ = normalize(tokenize(code_a))
        tokens_b, _ = normalize(tokenize(code_b))
        score = cosine_similarity(tokens_a, tokens_b)
        assert score > 80.0

    def test_different_tokens(self):
        """Very different code should have lower cosine similarity."""
        code_a = "int x = 5;"
        code_b = "void print() { cout << hello; }"
        tokens_a = tokenize(code_a)
        tokens_b = tokenize(code_b)
        score = cosine_similarity(tokens_a, tokens_b)
        assert score < 80.0

    def test_symmetry(self):
        """cosine(A, B) should equal cosine(B, A)."""
        tokens_a = tokenize("int x = 5;")
        tokens_b = tokenize("float y = 3.14;")
        score_ab = cosine_similarity(tokens_a, tokens_b)
        score_ba = cosine_similarity(tokens_b, tokens_a)
        assert score_ab == pytest.approx(score_ba, abs=0.01)
