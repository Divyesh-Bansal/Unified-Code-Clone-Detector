"""Tests for the variable normalizer module."""

import pytest
from my_tool.tokenizer import Token, tokenize
from my_tool.normalizer import normalize


class TestNormalize:
    """Tests for the normalize() function."""

    def test_invalid_input(self):
        with pytest.raises(TypeError):
            normalize("not a list")

    def test_empty_list(self):
        tokens, dictionary = normalize([])
        assert tokens == []
        assert dictionary == {}

    def test_single_identifier(self):
        tokens = [Token('IDENTIFIER', 'myVar', 1, 1)]
        result, dictionary = normalize(tokens)
        assert len(result) == 1
        assert result[0].value == 'id0'
        assert dictionary == {'myVar': 'id0'}

    def test_multiple_identifiers(self):
        tokens = [
            Token('IDENTIFIER', 'x', 1, 1),
            Token('IDENTIFIER', 'y', 1, 3),
            Token('IDENTIFIER', 'z', 1, 5),
        ]
        result, dictionary = normalize(tokens)
        assert result[0].value == 'id0'
        assert result[1].value == 'id1'
        assert result[2].value == 'id2'

    def test_repeated_identifiers_same_id(self):
        tokens = [
            Token('IDENTIFIER', 'x', 1, 1),
            Token('IDENTIFIER', 'y', 1, 3),
            Token('IDENTIFIER', 'x', 2, 1),  # repeated
        ]
        result, dictionary = normalize(tokens)
        assert result[0].value == 'id0'
        assert result[1].value == 'id1'
        assert result[2].value == 'id0'  # same as first 'x'

    def test_non_identifiers_unchanged(self):
        tokens = [
            Token('KEYWORD', 'int', 1, 1),
            Token('IDENTIFIER', 'x', 1, 5),
            Token('OPERATOR', '=', 1, 7),
            Token('NUMERIC', '5', 1, 9),
        ]
        result, _ = normalize(tokens)
        assert result[0].value == 'int'  # keyword unchanged
        assert result[1].value == 'id0'  # identifier normalized
        assert result[2].value == '='    # operator unchanged
        assert result[3].value == '5'    # numeric unchanged

    def test_structural_equivalence(self):
        """Two functions with different variable names should normalize identically."""
        code_a = "int add(int a, int b) { return a + b; }"
        code_b = "int sum(int x, int y) { return x + y; }"

        tokens_a = tokenize(code_a)
        tokens_b = tokenize(code_b)

        norm_a, _ = normalize(tokens_a)
        norm_b, _ = normalize(tokens_b)

        values_a = [t.value for t in norm_a]
        values_b = [t.value for t in norm_b]

        assert values_a == values_b

    def test_dictionary_mapping(self):
        tokens = tokenize("int myVariable = otherVariable + 10;")
        _, dictionary = normalize(tokens)
        assert 'myVariable' in dictionary
        assert 'otherVariable' in dictionary
        assert dictionary['myVariable'] != dictionary['otherVariable']
