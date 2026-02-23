"""Tests for LexicalDetector module."""

import pytest
from my_tool.tokenizer import tokenize
from my_tool.normalizer import normalize
from my_tool.similarity.lexical import lexical_score


class TestLexicalScore:
    """Tests for lexical_score()."""

    def test_empty_inputs(self):
        result = lexical_score([], [])
        assert result['lexical'] == 0.0

    def test_identical_code(self):
        code = "int add(int a, int b) { return a + b; }"
        tokens = tokenize(code)
        norm, _ = normalize(tokens)
        result = lexical_score(norm, norm)
        assert result['lexical'] > 90.0
        assert result['cosine'] == pytest.approx(100.0, abs=0.1)
        assert result['lcs'] == pytest.approx(100.0, abs=0.1)

    def test_renamed_variables(self):
        """Same structure, different var names → high lexical score after normalization."""
        code_a = "int add(int a, int b) { return a + b; }"
        code_b = "int sum(int x, int y) { return x + y; }"

        norm_a, _ = normalize(tokenize(code_a))
        norm_b, _ = normalize(tokenize(code_b))
        result = lexical_score(norm_a, norm_b)
        assert result['lexical'] > 80.0

    def test_different_code(self):
        """Structurally different code → lower score."""
        code_a = "int add(int a, int b) { return a + b; }"
        code_b = """
        void sort(int arr[], int n) {
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    if (arr[i] < arr[j]) {
                        int tmp = arr[i];
                        arr[i] = arr[j];
                        arr[j] = tmp;
                    }
                }
            }
        }
        """
        norm_a, _ = normalize(tokenize(code_a))
        norm_b, _ = normalize(tokenize(code_b))
        result = lexical_score(norm_a, norm_b)
        assert result['lexical'] < 50.0

    def test_all_scores_present(self):
        """Result should contain all expected keys."""
        tokens = tokenize("int x = 5;")
        result = lexical_score(tokens, tokens)
        assert 'cosine' in result
        assert 'lcs' in result
        assert 'weight' in result
        assert 'lexical' in result

    def test_weight_different_sizes(self):
        """Weight should be < 100% for different sized methods."""
        code_a = "int f() { return 0; }"
        code_b = "int g(int x, int y) { int z = x + y; return z; }"
        norm_a, _ = normalize(tokenize(code_a))
        norm_b, _ = normalize(tokenize(code_b))
        result = lexical_score(norm_a, norm_b)
        assert result['weight'] < 100.0
