"""Tests for the Java tokenizer module."""

import os
import tempfile
import pytest
from my_tool.java_tokenizer import tokenize_java, tokenize_java_file, Token


class TestTokenizeJava:
    """Tests for the tokenize_java() function."""

    def test_empty_string(self):
        assert tokenize_java("") == []

    def test_whitespace_only(self):
        assert tokenize_java("   \n\t  ") == []

    def test_invalid_input_type(self):
        with pytest.raises(TypeError):
            tokenize_java(123)

    def test_simple_variable_declaration(self):
        tokens = tokenize_java("int x = 5;")
        assert len(tokens) == 5  # int x = 5 ;
        assert tokens[0] == Token('DATATYPE', 'int', 1, 1)
        assert tokens[1] == Token('IDENTIFIER', 'x', 1, 5)
        assert tokens[2] == Token('OPERATOR', '=', 1, 7)
        assert tokens[3] == Token('NUMERIC', '5', 1, 9)
        assert tokens[4] == Token('SEMICOLON', ';', 1, 10)

    def test_java_keywords_identified(self):
        tokens = tokenize_java("if (x > 0) return true;")
        keyword_tokens = [t for t in tokens if t.type == 'KEYWORD']
        assert any(t.value == 'if' for t in keyword_tokens)
        assert any(t.value == 'return' for t in keyword_tokens)
        assert any(t.value == 'true' for t in keyword_tokens)

    def test_java_specific_keywords(self):
        tokens = tokenize_java("public static final synchronized")
        assert all(t.type == 'KEYWORD' for t in tokens)
        values = [t.value for t in tokens]
        assert 'public' in values
        assert 'static' in values
        assert 'final' in values
        assert 'synchronized' in values

    def test_java_datatypes(self):
        tokens = tokenize_java("int float double boolean String")
        assert all(t.type == 'DATATYPE' for t in tokens)

    def test_java_wrapper_types(self):
        tokens = tokenize_java("Integer Long Float Double Boolean")
        assert all(t.type == 'DATATYPE' for t in tokens)

    def test_java_collection_types(self):
        tokens = tokenize_java("List Map Set ArrayList HashMap")
        assert all(t.type == 'DATATYPE' for t in tokens)

    def test_identifiers(self):
        tokens = tokenize_java("myVar _private camelCase")
        assert all(t.type == 'IDENTIFIER' for t in tokens)

    def test_numeric_literals(self):
        tokens = tokenize_java("42 3.14 0xFF 1e10 100L 3.14f")
        assert all(t.type == 'NUMERIC' for t in tokens)

    def test_string_literals(self):
        tokens = tokenize_java('"hello world"')
        assert len(tokens) == 1
        assert tokens[0].type == 'STRING'

    def test_char_literals(self):
        tokens = tokenize_java("'a' 'b'")
        assert len(tokens) == 2
        assert all(t.type == 'CHAR' for t in tokens)

    def test_operators(self):
        tokens = tokenize_java("+ - * / == != <= >= && ||")
        assert all(t.type == 'OPERATOR' for t in tokens)

    def test_annotations_discarded(self):
        code = "@Override\npublic void test() { }"
        tokens = tokenize_java(code)
        for t in tokens:
            assert t.type != 'ANNOTATION'
        # Should still have the method tokens
        values = [t.value for t in tokens]
        assert 'public' in values
        assert 'test' in values

    def test_annotation_with_params_discarded(self):
        code = '@SuppressWarnings("unchecked")\npublic void test() { }'
        tokens = tokenize_java(code)
        for t in tokens:
            assert t.type != 'ANNOTATION'

    def test_comments_discarded(self):
        code = """
        int x = 5; // this is a comment
        /* block comment */
        int y = 10;
        """
        tokens = tokenize_java(code)
        for t in tokens:
            assert t.type not in ('LINE_COMMENT', 'BLOCK_COMMENT')

    def test_line_numbers(self):
        code = "int x;\nint y;"
        tokens = tokenize_java(code)
        assert tokens[0].line == 1  # int
        assert tokens[1].line == 1  # x

    def test_complete_method(self):
        code = """
        public int add(int a, int b) {
            return a + b;
        }
        """
        tokens = tokenize_java(code)
        assert len(tokens) > 0
        values = [t.value for t in tokens]
        assert 'add' in values
        assert 'return' in values

    def test_delimiters(self):
        tokens = tokenize_java("( ) { } [ ] ; ,")
        types = [t.type for t in tokens]
        assert 'LPAREN' in types
        assert 'RPAREN' in types
        assert 'LBRACE' in types
        assert 'RBRACE' in types
        assert 'SEMICOLON' in types
        assert 'COMMA' in types


class TestTokenizeJavaFile:
    """Tests for the tokenize_java_file() function."""

    def test_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            tokenize_java_file("/nonexistent/path/File.java")

    def test_sample_file(self):
        sample_dir = os.path.join(os.path.dirname(__file__), '..', 'test_input')
        filepath = os.path.join(sample_dir, 'sample_java_duplicate.java')
        if os.path.exists(filepath):
            tokens = tokenize_java_file(filepath)
            assert len(tokens) > 0
            values = [t.value for t in tokens]
            assert 'addNumbers' in values
            assert 'sumValues' in values

    def test_temp_file(self):
        code = "public class Test { public int foo() { return 1; } }"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java',
                                          delete=False, encoding='utf-8') as f:
            f.write(code)
            tmppath = f.name
        try:
            tokens = tokenize_java_file(tmppath)
            assert len(tokens) > 0
            values = [t.value for t in tokens]
            assert 'foo' in values
        finally:
            os.unlink(tmppath)
