"""Tests for the C++ tokenizer module."""

import os
import pytest
from my_tool.tokenizer import tokenize, tokenize_file, Token


class TestTokenize:
    """Tests for the tokenize() function."""

    def test_empty_string(self):
        assert tokenize("") == []

    def test_whitespace_only(self):
        assert tokenize("   \n\t  ") == []

    def test_invalid_input_type(self):
        with pytest.raises(TypeError):
            tokenize(123)

    def test_simple_variable_declaration(self):
        tokens = tokenize("int x = 5;")
        assert len(tokens) == 5  # int x = 5 ;
        assert tokens[0] == Token('DATATYPE', 'int', 1, 1)
        assert tokens[1] == Token('IDENTIFIER', 'x', 1, 5)
        assert tokens[2] == Token('OPERATOR', '=', 1, 7)
        assert tokens[3] == Token('NUMERIC', '5', 1, 9)
        assert tokens[4] == Token('SEMICOLON', ';', 1, 10)

    def test_keywords_identified(self):
        tokens = tokenize("if (x > 0) return true;")
        keyword_tokens = [t for t in tokens if t.type == 'KEYWORD']
        assert any(t.value == 'if' for t in keyword_tokens)
        assert any(t.value == 'return' for t in keyword_tokens)
        assert any(t.value == 'true' for t in keyword_tokens)

    def test_datatypes_identified(self):
        tokens = tokenize("int float double char bool void")
        assert all(t.type == 'DATATYPE' for t in tokens)

    def test_identifiers(self):
        tokens = tokenize("myVar _private camelCase")
        assert all(t.type == 'IDENTIFIER' for t in tokens)

    def test_numeric_literals(self):
        tokens = tokenize("42 3.14 0xFF 1e10")
        assert all(t.type == 'NUMERIC' for t in tokens)
        assert len(tokens) == 4

    def test_string_literals(self):
        tokens = tokenize('"hello world"')
        assert len(tokens) == 1
        assert tokens[0].type == 'STRING'

    def test_char_literals(self):
        tokens = tokenize("'a' 'b'")
        assert len(tokens) == 2
        assert all(t.type == 'CHAR' for t in tokens)

    def test_operators(self):
        tokens = tokenize("+ - * / == != <= >= && ||")
        assert all(t.type == 'OPERATOR' for t in tokens)

    def test_delimiters(self):
        tokens = tokenize("( ) { } [ ] ; ,")
        types = [t.type for t in tokens]
        assert 'LPAREN' in types
        assert 'RPAREN' in types
        assert 'LBRACE' in types
        assert 'RBRACE' in types
        assert 'SEMICOLON' in types
        assert 'COMMA' in types

    def test_comments_discarded(self):
        code = """
        int x = 5; // this is a comment
        /* block comment */
        int y = 10;
        """
        tokens = tokenize(code)
        # Comments should be removed
        for t in tokens:
            assert t.type not in ('LINE_COMMENT', 'BLOCK_COMMENT')

    def test_preprocessor_discarded(self):
        tokens = tokenize("#include <iostream>\nint x;")
        for t in tokens:
            assert t.type != 'PREPROCESSOR'

    def test_line_numbers(self):
        code = "int x;\nint y;"
        tokens = tokenize(code)
        # First line tokens
        assert tokens[0].line == 1  # int
        assert tokens[1].line == 1  # x

    def test_complete_function(self):
        code = """
        int add(int a, int b) {
            return a + b;
        }
        """
        tokens = tokenize(code)
        assert len(tokens) > 0
        # Should contain: int, add, (, int, a, ,, int, b, ), {, return, a, +, b, ;, }
        values = [t.value for t in tokens]
        assert 'add' in values
        assert 'return' in values

    def test_escaped_string(self):
        tokens = tokenize(r'"hello \"world\""')
        assert len(tokens) == 1
        assert tokens[0].type == 'STRING'


class TestTokenizeFile:
    """Tests for the tokenize_file() function."""

    def test_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            tokenize_file("/nonexistent/path/file.cpp")

    def test_sample_file(self):
        sample_dir = os.path.join(os.path.dirname(__file__), 'sample_files')
        filepath = os.path.join(sample_dir, 'simple_duplicate.cpp')
        if os.path.exists(filepath):
            tokens = tokenize_file(filepath)
            assert len(tokens) > 0
            # Should find function names
            values = [t.value for t in tokens]
            assert 'printArray' in values
            assert 'displayArray' in values
