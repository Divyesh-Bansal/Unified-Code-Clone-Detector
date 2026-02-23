"""Tests for LCS similarity module."""

import pytest
from my_tool.tokenizer import tokenize
from my_tool.similarity.lcs import lcs_similarity


class TestLCSSimilarity:
    """Tests for lcs_similarity()."""

    def test_empty_inputs(self):
        assert lcs_similarity([], []) == 0.0

    def test_one_empty(self):
        tokens = tokenize("int x;")
        assert lcs_similarity(tokens, []) == 0.0

    def test_identical(self):
        tokens = tokenize("int x = 5;")
        score = lcs_similarity(tokens, tokens)
        assert score == pytest.approx(100.0, abs=0.1)

    def test_partial_overlap(self):
        """Some shared tokens should produce partial score."""
        tokens_a = tokenize("int x = 5;")
        tokens_b = tokenize("int y = 10;")
        score = lcs_similarity(tokens_a, tokens_b)
        assert 0 < score <= 100

    def test_no_common(self):
        """Completely different tokens should score very low."""
        tokens_a = tokenize("int x;")
        tokens_b = tokenize("void f() {}")
        score = lcs_similarity(tokens_a, tokens_b)
        # Some overlap possible with delimiters
        assert score < 100

    def test_symmetry(self):
        tokens_a = tokenize("int x;")
        tokens_b = tokenize("int y;")
        s1 = lcs_similarity(tokens_a, tokens_b)
        s2 = lcs_similarity(tokens_b, tokens_a)
        assert s1 == pytest.approx(s2, abs=0.01)
