"""Tests for report generation module."""

import os
import tempfile
import pytest

from my_tool.similarity.hybrid import SimilarityResult
from my_tool.report import MethodPairResult, generate_report, format_console_output


def _make_result(lexical=70.0, structural=50.0, semantic=80.0):
    """Helper to create a SimilarityResult."""
    hybrid = lexical * 0.50 + structural * 0.35 + semantic * 0.15
    confidence = "HIGH" if hybrid > 75 else "MEDIUM" if hybrid > 60 else "LOW"
    return SimilarityResult(
        lexical_score=lexical,
        structural_score=structural,
        semantic_score=semantic,
        hybrid_score=round(hybrid, 2),
        confidence=confidence,
        details={}
    )


class TestGenerateReport:
    """Tests for generate_report()."""

    def test_empty_results(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                          delete=False) as f:
            outpath = f.name

        try:
            path = generate_report([], "./test", 60.0,
                                   output_path=outpath)
            assert os.path.exists(path)
            with open(path, encoding='utf-8') as f:
                content = f.read()
            assert "No similar function pairs found" in content
        finally:
            os.unlink(outpath)

    def test_report_with_results(self):
        result = _make_result()
        pairs = [
            MethodPairResult("a.cpp", "funcA", 1, "b.cpp", "funcB", 5, result)
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                          delete=False) as f:
            outpath = f.name

        try:
            path = generate_report(pairs, "./test", 60.0,
                                   output_path=outpath,
                                   total_files=2,
                                   total_functions=4)
            assert os.path.exists(path)
            with open(path, encoding='utf-8') as f:
                content = f.read()
            assert "funcA" in content
            assert "funcB" in content
            assert "LexicalDetector" in content
            assert "StructuralDetector" in content
            assert "SemanticDetector" in content
            assert "HYBRID SCORE" in content
        finally:
            os.unlink(outpath)

    def test_report_contains_statistics(self):
        result = _make_result()
        pairs = [
            MethodPairResult("a.cpp", "f", 1, "b.cpp", "g", 2, result),
            MethodPairResult("c.cpp", "h", 3, "d.cpp", "k", 4, result),
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                          delete=False) as f:
            outpath = f.name

        try:
            generate_report(pairs, "./test", 60.0, output_path=outpath)
            with open(path := outpath, encoding='utf-8') as f:
                content = f.read()
            assert "SUMMARY" in content
            assert "Confidence Distribution" in content
        finally:
            os.unlink(outpath)


class TestFormatConsoleOutput:
    """Tests for format_console_output()."""

    def test_no_results(self):
        output = format_console_output([], "./test", 60.0)
        assert "No similar function pairs found" in output

    def test_with_results(self):
        result = _make_result()
        pairs = [
            MethodPairResult("a.cpp", "funcA", 1, "b.cpp", "funcB", 5, result)
        ]
        output = format_console_output(pairs, "./test", 60.0,
                                       total_files=2, total_functions=4)
        assert "funcA" in output
        assert "funcB" in output
        assert "HYBRID SCORE" in output
