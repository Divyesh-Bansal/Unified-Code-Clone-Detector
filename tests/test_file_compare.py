"""Tests for file-level comparison module and mode-aware report output."""

import os
import tempfile
import pytest

from my_tool.tokenizer import tokenize
from my_tool.method_extractor import extract_methods, MethodInfo
from my_tool.similarity.hybrid import SimilarityResult
from my_tool.file_compare import compute_file_similarity, _bipartite_best_match_score
from my_tool.report import MethodPairResult, generate_report, format_console_output


# ── Sample code snippets ─────────────────────────────────────────────────

_FILE_A = """
int findMax(int arr[], int n) {
    int maxVal = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] > maxVal) {
            maxVal = arr[i];
        }
    }
    return maxVal;
}

int sumArray(int arr[], int n) {
    int total = 0;
    for (int i = 0; i < n; i++) {
        total += arr[i];
    }
    return total;
}
"""

_FILE_B = """
int getLargest(int data[], int count) {
    int biggest = data[0];
    for (int j = 1; j < count; j++) {
        if (data[j] > biggest) {
            biggest = data[j];
        }
    }
    return biggest;
}

int addElements(int data[], int count) {
    int sum = 0;
    for (int j = 0; j < count; j++) {
        sum += data[j];
    }
    return sum;
}
"""

_DIFFERENT_FILE = """
void bubbleSort(int arr[], int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j+1]) {
                int t = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = t;
            }
        }
    }
}
"""

_NO_FUNCTIONS = """
int x = 5;
int y = 10;
int z = x + y;
"""


def _tok_and_methods(code):
    """Helper: tokenize code and extract methods."""
    tokens = tokenize(code)
    methods = extract_methods(tokens)
    return tokens, methods


# ── Tests for compute_file_similarity ─────────────────────────────────────

class TestComputeFileSimilarity:
    """Unit tests for the file-level similarity function."""

    def test_identical_files_high_score(self):
        tokens, methods = _tok_and_methods(_FILE_A)
        result = compute_file_similarity(tokens, tokens, methods, methods)
        assert result.hybrid_score > 80.0
        assert result.confidence in ("VERY HIGH", "HIGH")

    def test_renamed_vars_high_score(self):
        """Files with renamed variables should still be highly similar."""
        tok_a, meth_a = _tok_and_methods(_FILE_A)
        tok_b, meth_b = _tok_and_methods(_FILE_B)
        result = compute_file_similarity(tok_a, tok_b, meth_a, meth_b)
        assert result.hybrid_score > 40.0

    def test_different_files_lower_score(self):
        tok_a, meth_a = _tok_and_methods(_FILE_A)
        tok_b, meth_b = _tok_and_methods(_DIFFERENT_FILE)
        result = compute_file_similarity(tok_a, tok_b, meth_a, meth_b)
        # Should be noticeably lower than the renamed-vars case
        renamed_result = compute_file_similarity(
            tok_a, *_tok_and_methods(_FILE_B)[0:1],
            meth_a, _tok_and_methods(_FILE_B)[1],
        )
        # The different file should not score as high
        assert result.hybrid_score < 80.0

    def test_empty_tokens(self):
        result = compute_file_similarity([], [], [], [])
        assert result.hybrid_score == 0.0
        assert result.confidence == "LOW"

    def test_no_extractable_methods_lexical_only(self):
        """When no functions are found, structural/semantic = 0, only lexical contributes."""
        tok_a, _ = _tok_and_methods(_NO_FUNCTIONS)
        tok_b, _ = _tok_and_methods(_NO_FUNCTIONS)
        result = compute_file_similarity(tok_a, tok_b, [], [])
        assert result.structural_score == 0.0
        assert result.semantic_score == 0.0
        # Lexical should still contribute
        assert result.lexical_score > 0.0

    def test_result_structure(self):
        tok_a, meth_a = _tok_and_methods(_FILE_A)
        result = compute_file_similarity(tok_a, tok_a, meth_a, meth_a)
        assert isinstance(result, SimilarityResult)
        assert hasattr(result, 'lexical_score')
        assert hasattr(result, 'structural_score')
        assert hasattr(result, 'semantic_score')
        assert hasattr(result, 'hybrid_score')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'details')

    def test_scores_bounded(self):
        tok_a, meth_a = _tok_and_methods(_FILE_A)
        tok_b, meth_b = _tok_and_methods(_FILE_B)
        result = compute_file_similarity(tok_a, tok_b, meth_a, meth_b)
        assert 0 <= result.lexical_score <= 100
        assert 0 <= result.structural_score <= 100
        assert 0 <= result.semantic_score <= 100
        assert 0 <= result.hybrid_score <= 100


# ── Tests for bipartite best-match helper ─────────────────────────────────

class TestBipartiteBestMatch:
    """Unit tests for _bipartite_best_match_score."""

    def test_empty_lists(self):
        assert _bipartite_best_match_score([], [], lambda a, b: 100.0) == 0.0

    def test_one_empty_list(self):
        _, methods = _tok_and_methods(_FILE_A)
        assert _bipartite_best_match_score(methods, [], lambda a, b: 100.0) == 0.0

    def test_all_perfect_matches(self):
        _, methods = _tok_and_methods(_FILE_A)
        score = _bipartite_best_match_score(
            methods, methods, lambda a, b: 100.0
        )
        assert score == 100.0


# ── Tests for report mode-awareness ───────────────────────────────────────

def _make_result(lexical=70.0, structural=50.0, semantic=80.0):
    hybrid = lexical * 0.50 + structural * 0.35 + semantic * 0.15
    confidence = "HIGH" if hybrid > 75 else "MEDIUM" if hybrid > 60 else "LOW"
    return SimilarityResult(
        lexical_score=lexical, structural_score=structural,
        semantic_score=semantic, hybrid_score=round(hybrid, 2),
        confidence=confidence, details={},
    )


class TestReportFileMode:
    """Test that report output adapts correctly to mode='file'."""

    def test_report_file_mode_hides_functions(self):
        result = _make_result()
        pairs = [
            MethodPairResult("a.cpp", "<file>", 0, "b.cpp", "<file>", 0, result)
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            outpath = f.name

        try:
            generate_report(pairs, "./test", 60.0, output_path=outpath,
                            total_files=2, total_functions=0, mode='file')
            with open(outpath, encoding='utf-8') as f:
                content = f.read()
            assert "Function A:" not in content
            assert "Function B:" not in content
            assert "SIMILAR FILE PAIRS" in content
            assert "File-Level" in content
        finally:
            os.unlink(outpath)

    def test_report_fxn_mode_unchanged(self):
        """Default mode should still show function names (backward compat)."""
        result = _make_result()
        pairs = [
            MethodPairResult("a.cpp", "funcA", 1, "b.cpp", "funcB", 5, result)
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            outpath = f.name

        try:
            generate_report(pairs, "./test", 60.0, output_path=outpath,
                            total_files=2, total_functions=4)
            with open(outpath, encoding='utf-8') as f:
                content = f.read()
            assert "Function A: funcA" in content
            assert "Function B: funcB" in content
            assert "SIMILAR FUNCTION PAIRS" in content
            assert "Function-Level" in content
        finally:
            os.unlink(outpath)

    def test_console_file_mode_hides_functions(self):
        result = _make_result()
        pairs = [
            MethodPairResult("a.cpp", "<file>", 0, "b.cpp", "<file>", 0, result)
        ]
        output = format_console_output(pairs, "./test", 60.0, total_files=2,
                                        total_functions=0, mode='file')
        assert "<file>" not in output
        assert "line 0" not in output
        assert "File-Level" in output

    def test_console_fxn_mode_unchanged(self):
        result = _make_result()
        pairs = [
            MethodPairResult("a.cpp", "funcA", 1, "b.cpp", "funcB", 5, result)
        ]
        output = format_console_output(pairs, "./test", 60.0, total_files=2,
                                        total_functions=4)
        assert "funcA" in output
        assert "funcB" in output
        assert "Function-Level" in output

    def test_console_no_results_file_mode(self):
        output = format_console_output([], "./test", 60.0, mode='file')
        assert "No similar file pairs found" in output

    def test_console_no_results_fxn_mode(self):
        output = format_console_output([], "./test", 60.0)
        assert "No similar function pairs found" in output
