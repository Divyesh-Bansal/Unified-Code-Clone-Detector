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

    def test_order_sensitivity(self):
        """Trigram cosine should be sensitive to token order.
        Same tokens in a different arrangement should NOT score 100%."""
        # Same structural tokens but swapped assignment targets
        tokens_a = tokenize("int x = a + b; int y = c;")
        tokens_b = tokenize("int y = a + b; int x = c;")
        score = cosine_similarity(tokens_a, tokens_b)
        # Shared tokens are the same, but trigram profiles differ
        assert score < 100.0
        # Still reasonably similar (many overlapping trigrams)
        assert score > 20.0

    def test_short_method_fallback(self):
        """Methods with < 3 tokens should still produce a valid score
        via bigram/unigram fallback."""
        tokens_a = tokenize("x;")
        tokens_b = tokenize("x;")
        score = cosine_similarity(tokens_a, tokens_b)
        assert score == pytest.approx(100.0, abs=0.1)

    def test_renamed_normalized_high(self):
        """Same structure, different variable names → high score
        after normalization (validates end-to-end pipeline)."""
        code_a = "int add(int a, int b) { return a + b; }"
        code_b = "int sum(int x, int y) { return x + y; }"
        norm_a, _ = normalize(tokenize(code_a))
        norm_b, _ = normalize(tokenize(code_b))
        score = cosine_similarity(norm_a, norm_b)
        assert score > 80.0
