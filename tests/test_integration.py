"""Integration tests - full pipeline from files to results."""

import os
import tempfile
import pytest

from my_tool.main import find_cpp_files, extract_all_methods, compare_all_methods
from my_tool.report import generate_report


SAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'sample_files')


class TestFindCppFiles:
    """Tests for find_cpp_files()."""

    def test_nonexistent_path(self):
        with pytest.raises(FileNotFoundError):
            find_cpp_files("/nonexistent/path")

    def test_non_cpp_file(self):
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(b"print('hello')")
            tmppath = f.name
        try:
            with pytest.raises(ValueError):
                find_cpp_files(tmppath)
        finally:
            os.unlink(tmppath)

    def test_find_in_directory(self):
        if os.path.exists(SAMPLE_DIR):
            files = find_cpp_files(SAMPLE_DIR)
            assert len(files) >= 4
            assert all(f.endswith(('.cpp', '.h', '.hpp', '.cc', '.cxx'))
                       for f in files)

    def test_single_file(self):
        filepath = os.path.join(SAMPLE_DIR, 'simple_duplicate.cpp')
        if os.path.exists(filepath):
            files = find_cpp_files(filepath)
            assert len(files) == 1


class TestExtractAllMethods:
    """Tests for extract_all_methods()."""

    def test_extract_from_sample(self):
        filepath = os.path.join(SAMPLE_DIR, 'simple_duplicate.cpp')
        if os.path.exists(filepath):
            methods = extract_all_methods([filepath])
            assert len(methods) >= 2
            names = [m[1].name for m in methods]
            assert 'printArray' in names
            assert 'displayArray' in names

    def test_empty_file_list(self):
        methods = extract_all_methods([])
        assert methods == []

    def test_nonexistent_file_handled(self):
        """Should print warning but not crash."""
        methods = extract_all_methods(["/nonexistent/file.cpp"])
        assert methods == []


class TestCompareAllMethods:
    """Tests for compare_all_methods()."""

    def test_duplicates_detected(self):
        filepath = os.path.join(SAMPLE_DIR, 'simple_duplicate.cpp')
        if os.path.exists(filepath):
            methods = extract_all_methods([filepath])
            results = compare_all_methods(methods, 40.0)
            assert len(results) > 0
            # At least one pair should be found
            func_pairs = [(r.func_a, r.func_b) for r in results]
            # printArray/displayArray or sumArray/addElements should be similar
            all_funcs = set()
            for a, b in func_pairs:
                all_funcs.add(a)
                all_funcs.add(b)
            assert len(all_funcs) >= 2

    def test_high_threshold_fewer_results(self):
        filepath = os.path.join(SAMPLE_DIR, 'simple_duplicate.cpp')
        if os.path.exists(filepath):
            methods = extract_all_methods([filepath])
            results_low = compare_all_methods(methods, 30.0)
            results_high = compare_all_methods(methods, 90.0)
            assert len(results_high) <= len(results_low)


class TestFullPipeline:
    """End-to-end integration tests."""

    def test_full_pipeline_sample_dir(self):
        if not os.path.exists(SAMPLE_DIR):
            pytest.skip("Sample directory not found")

        files = find_cpp_files(SAMPLE_DIR)
        methods = extract_all_methods(files)
        results = compare_all_methods(methods, 40.0)

        # Generate report
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                          delete=False) as f:
            outpath = f.name

        try:
            report_path = generate_report(
                results, SAMPLE_DIR, 40.0,
                output_path=outpath,
                total_files=len(files),
                total_functions=len(methods)
            )
            assert os.path.exists(report_path)
            with open(report_path) as f:
                content = f.read()
            assert "HYBRID CODE CLONE DETECTION" in content
        finally:
            os.unlink(outpath)

    def test_renamed_vars_detection(self):
        """Functions with only renamed variables should be detected as similar."""
        filepath = os.path.join(SAMPLE_DIR, 'renamed_vars.cpp')
        if not os.path.exists(filepath):
            pytest.skip("renamed_vars.cpp not found")

        methods = extract_all_methods([filepath])
        assert len(methods) >= 2

        results = compare_all_methods(methods, 40.0)
        assert len(results) > 0

        # findMax and getLargest should be a similar pair
        found = False
        for r in results:
            names = {r.func_a, r.func_b}
            if 'findMax' in names and 'getLargest' in names:
                found = True
                assert r.result.hybrid_score > 40.0
                break
        assert found, "findMax/getLargest pair not detected"
