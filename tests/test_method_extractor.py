"""Tests for the method extractor module."""

import pytest
from my_tool.tokenizer import tokenize
from my_tool.method_extractor import extract_methods


class TestExtractMethods:
    """Tests for the extract_methods() function."""

    def test_invalid_input(self):
        with pytest.raises(TypeError):
            extract_methods("not a list")

    def test_empty_list(self):
        assert extract_methods([]) == []

    def test_single_function(self):
        code = "int add(int a, int b) { return a + b; }"
        tokens = tokenize(code)
        methods = extract_methods(tokens)
        assert len(methods) == 1
        assert methods[0].name == 'add'
        assert methods[0].return_type == 'int'
        assert methods[0].param_count == 2

    def test_void_function(self):
        code = "void print() { cout << 1; }"
        tokens = tokenize(code)
        methods = extract_methods(tokens)
        assert len(methods) == 1
        assert methods[0].name == 'print'
        assert methods[0].return_type == 'void'

    def test_no_params(self):
        code = "int getZero() { return 0; }"
        tokens = tokenize(code)
        methods = extract_methods(tokens)
        assert len(methods) == 1
        assert methods[0].param_count == 0

    def test_multiple_functions(self):
        code = """
        int add(int a, int b) { return a + b; }
        int sub(int a, int b) { return a - b; }
        void print(int x) { cout << x; }
        """
        tokens = tokenize(code)
        methods = extract_methods(tokens)
        assert len(methods) == 3
        names = [m.name for m in methods]
        assert 'add' in names
        assert 'sub' in names
        assert 'print' in names

    def test_nested_braces(self):
        code = """
        int func(int n) {
            if (n > 0) {
                for (int i = 0; i < n; i++) {
                    cout << i;
                }
            }
            return n;
        }
        """
        tokens = tokenize(code)
        methods = extract_methods(tokens)
        assert len(methods) == 1
        assert methods[0].name == 'func'

    def test_no_functions(self):
        code = "int x = 5; float y = 3.14;"
        tokens = tokenize(code)
        methods = extract_methods(tokens)
        assert len(methods) == 0

    def test_function_line_numbers(self):
        code = "int add(int a, int b) {\n    return a + b;\n}"
        tokens = tokenize(code)
        methods = extract_methods(tokens)
        assert len(methods) == 1
        assert methods[0].start_line == 1
