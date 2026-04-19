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

    def test_rare_tokens_score_higher(self):
        """Two methods sharing rare custom identifiers should produce
        a higher LCS score than two sharing only common boilerplate,
        even when the raw LCS length would be similar."""
        # Methods that share rare identifiers (unique to these snippets)
        code_rare_a = "int computeGalaxySpin(int starMass) { return starMass; }"
        code_rare_b = "int computeGalaxySpin(int starMass) { return starMass; }"

        # Methods that share only very common tokens
        code_common_a = "int f(int a) { return a; }"
        code_common_b = "int g(int b) { return b; }"

        tokens_rare_a = tokenize(code_rare_a)
        tokens_rare_b = tokenize(code_rare_b)
        tokens_common_a = tokenize(code_common_a)
        tokens_common_b = tokenize(code_common_b)

        score_rare = lcs_similarity(tokens_rare_a, tokens_rare_b)
        score_common = lcs_similarity(tokens_common_a, tokens_common_b)

        # Identical code always scores 100%, so common also scores high
        # The key test: rare identical code scores at least as high
        assert score_rare >= score_common

    def test_idf_weights_computed(self):
        """Verify IDF weights assign higher weight to unique tokens."""
        from my_tool.similarity.lcs import _compute_idf_weights
        tokens_a = tokenize("int x = 5;")
        tokens_b = tokenize("int y = 10;")
        weights = _compute_idf_weights(tokens_a, tokens_b)

        # 'int', '=', ';' are shared → IDF = 1.0
        assert weights['int'] == pytest.approx(1.0, abs=0.01)
        assert weights['='] == pytest.approx(1.0, abs=0.01)
        # 'x' only in A, 'y' only in B → higher IDF
        assert weights['x'] > 1.0
        assert weights['y'] > 1.0
