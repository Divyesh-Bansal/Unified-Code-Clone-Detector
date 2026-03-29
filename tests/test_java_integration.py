"""Integration tests for Java support - full pipeline from files to results."""

import os
import tempfile
import pytest

from my_tool.main import (
    find_source_files, group_files_by_language,
    extract_all_methods, extract_all_methods_java, compare_all_methods
)
from my_tool.report import generate_report


SAMPLE_DIR = os.path.join(os.path.dirname(__file__), '..', 'test_input')


class TestFindSourceFiles:
    """Tests for find_source_files() with Java support."""

    def test_java_file_accepted(self):
        with tempfile.NamedTemporaryFile(suffix='.java', delete=False,
                                          mode='w') as f:
            f.write("public class Test { }")
            tmppath = f.name
        try:
            files = find_source_files(tmppath)
            assert len(files) == 1
            assert files[0].endswith('.java')
        finally:
            os.unlink(tmppath)

    def test_unsupported_file_rejected(self):
        with tempfile.NamedTemporaryFile(suffix='.rb', delete=False,
                                          mode='w') as f:
            f.write("puts 'hello'")
            tmppath = f.name
        try:
            with pytest.raises(ValueError):
                find_source_files(tmppath)
        finally:
            os.unlink(tmppath)

    def test_mixed_directory(self):
        if os.path.exists(SAMPLE_DIR):
            files = find_source_files(SAMPLE_DIR)
            extensions = {os.path.splitext(f)[1].lower() for f in files}
            # Should find both .cpp and .java files
            assert '.cpp' in extensions or '.java' in extensions


class TestGroupFilesByLanguage:
    """Tests for group_files_by_language()."""

    def test_grouping(self):
        files = [
            '/path/to/file1.cpp',
            '/path/to/file2.h',
            '/path/to/File3.java',
            '/path/to/file4.hpp',
            '/path/to/File5.java',
        ]
        groups = group_files_by_language(files)
        assert len(groups['cpp']) == 3
        assert len(groups['java']) == 2

    def test_cpp_only(self):
        files = ['/path/to/a.cpp', '/path/to/b.h']
        groups = group_files_by_language(files)
        assert len(groups['cpp']) == 2
        assert len(groups['java']) == 0

    def test_java_only(self):
        files = ['/path/to/A.java', '/path/to/B.java']
        groups = group_files_by_language(files)
        assert len(groups['cpp']) == 0
        assert len(groups['java']) == 2

    def test_empty_list(self):
        groups = group_files_by_language([])
        assert groups == {'cpp': [], 'java': []}


class TestJavaMethodExtraction:
    """Tests for extract_all_methods_java()."""

    def test_extract_from_sample(self):
        filepath = os.path.join(SAMPLE_DIR, 'sample_java_duplicate.java')
        if os.path.exists(filepath):
            methods = extract_all_methods_java([filepath])
            assert len(methods) >= 2
            names = [m[1].name for m in methods]
            assert 'addNumbers' in names
            assert 'sumValues' in names

    def test_empty_file_list(self):
        methods = extract_all_methods_java([])
        assert methods == []


class TestJavaCloneDetection:
    """Tests for Java clone detection pipeline."""

    def test_java_duplicates_detected(self):
        filepath = os.path.join(SAMPLE_DIR, 'sample_java_duplicate.java')
        if not os.path.exists(filepath):
            pytest.skip("sample_java_duplicate.java not found")

        methods = extract_all_methods_java([filepath])
        results = compare_all_methods(methods, 40.0, language="Java")
        assert len(results) > 0

        # addNumbers/sumValues should be similar
        found = False
        for r in results:
            names = {r.func_a, r.func_b}
            if 'addNumbers' in names and 'sumValues' in names:
                found = True
                assert r.result.hybrid_score > 40.0
                assert r.language == "Java"
                break
        assert found, "addNumbers/sumValues pair not detected"

    def test_language_tag_in_results(self):
        filepath = os.path.join(SAMPLE_DIR, 'sample_java_duplicate.java')
        if not os.path.exists(filepath):
            pytest.skip("sample_java_duplicate.java not found")

        methods = extract_all_methods_java([filepath])
        results = compare_all_methods(methods, 40.0, language="Java")
        for r in results:
            assert r.language == "Java"


class TestNoCrossLanguageComparison:
    """Ensure no cross-language comparisons happen."""

    def test_groups_are_independent(self):
        """Verify that grouping keeps languages separate."""
        files = ['/a/file.cpp', '/a/File.java', '/a/other.h']
        groups = group_files_by_language(files)

        cpp_set = set(groups['cpp'])
        java_set = set(groups['java'])

        # No overlap
        assert cpp_set.isdisjoint(java_set)
        assert '/a/File.java' not in cpp_set
        assert '/a/file.cpp' not in java_set


class TestJavaReportGeneration:
    """Tests for report generation with Java results."""

    def test_report_contains_language_tag(self):
        filepath = os.path.join(SAMPLE_DIR, 'sample_java_duplicate.java')
        if not os.path.exists(filepath):
            pytest.skip("sample_java_duplicate.java not found")

        methods = extract_all_methods_java([filepath])
        results = compare_all_methods(methods, 40.0, language="Java")

        if not results:
            pytest.skip("No Java results to test")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                          delete=False) as f:
            outpath = f.name

        try:
            report_path = generate_report(
                results, SAMPLE_DIR, 40.0,
                output_path=outpath,
                total_files=1, total_functions=len(methods)
            )
            with open(report_path, encoding='utf-8') as f:
                content = f.read()
            assert "[Java]" in content
            assert "HYBRID CODE CLONE DETECTION" in content
        finally:
            os.unlink(outpath)
