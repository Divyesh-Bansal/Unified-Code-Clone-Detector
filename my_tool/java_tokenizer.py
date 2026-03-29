"""
Java Tokenizer Module

Tokenizes Java source code into a stream of categorized tokens,
discarding comments, whitespace, and annotations.

Output format matches the C++ tokenizer (Token NamedTuple) so that
the downstream normalizer and detectors work without modification.
"""

import re
from typing import List

from my_tool.tokenizer import Token


# Java keywords (excluding types listed in JAVA_DATATYPES)
JAVA_KEYWORDS = frozenset([
    'abstract', 'assert', 'break', 'case', 'catch', 'class', 'const',
    'continue', 'default', 'do', 'else', 'enum', 'extends', 'final',
    'finally', 'for', 'goto', 'if', 'implements', 'import', 'instanceof',
    'interface', 'native', 'new', 'package', 'private', 'protected',
    'public', 'return', 'static', 'strictfp', 'super', 'switch',
    'synchronized', 'this', 'throw', 'throws', 'transient', 'try',
    'volatile', 'while',
    'true', 'false', 'null', 'void',
])

# Java data types (primitive + common library types)
JAVA_DATATYPES = frozenset([
    'boolean', 'byte', 'char', 'short', 'int', 'long', 'float', 'double',
    'String', 'Integer', 'Long', 'Float', 'Double', 'Boolean', 'Byte',
    'Short', 'Character', 'Object', 'Void',
    'List', 'ArrayList', 'LinkedList',
    'Map', 'HashMap', 'TreeMap', 'LinkedHashMap',
    'Set', 'HashSet', 'TreeSet',
    'Queue', 'Deque', 'Stack', 'Vector',
    'Collection', 'Collections', 'Arrays',
])

# Token patterns (order matters — first match wins)
_JAVA_TOKEN_PATTERNS = [
    # Multi-line comments
    ('BLOCK_COMMENT', r'/\*[\s\S]*?\*/'),
    # Single-line comments
    ('LINE_COMMENT', r'//[^\n]*'),
    # Annotations (discarded, similar to preprocessor)
    ('ANNOTATION', r'@[a-zA-Z_]\w*(?:\([^)]*\))?'),
    # String literals (handles escaped quotes)
    ('STRING', r'"(?:[^"\\]|\\.)*"'),
    # Character literals
    ('CHAR', r"'(?:[^'\\]|\\.)*'"),
    # Numeric literals (hex, float with suffix, binary, long, int)
    ('NUMERIC', r'0[xX][0-9a-fA-F]+[lL]?'
               r'|0[bB][01]+[lL]?'
               r'|[0-9]+\.[0-9]*(?:[eE][+-]?[0-9]+)?[fFdD]?'
               r'|\.[0-9]+(?:[eE][+-]?[0-9]+)?[fFdD]?'
               r'|[0-9]+[eE][+-]?[0-9]+[fFdD]?'
               r'|[0-9]+[fFdDlL]?'),
    # Identifiers (and keywords — distinguished later)
    ('IDENTIFIER', r'[a-zA-Z_]\w*'),
    # Multi-character operators
    ('OPERATOR', r'<<='
               r'|>>='
               r'|>>>='
               r'|<<|>>>|>>'
               r'|\+\+|--|->'
               r'|&&|\|\||<=>|::'
               r'|[+\-*/%&|^~!<>=]=?'
               r'|\?|:'),
    # Delimiters
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('LBRACKET', r'\['),
    ('RBRACKET', r'\]'),
    ('SEMICOLON', r';'),
    ('COMMA', r','),
    ('DOT', r'\.'),
    # Whitespace (to be discarded)
    ('WHITESPACE', r'\s+'),
    # Anything else
    ('UNKNOWN', r'.'),
]

# Compile the master regex
_JAVA_MASTER_PATTERN = re.compile(
    '|'.join(f'(?P<{name}>{pattern})' for name, pattern in _JAVA_TOKEN_PATTERNS),
    re.DOTALL
)

# Token types to discard
_JAVA_DISCARD_TYPES = frozenset([
    'BLOCK_COMMENT', 'LINE_COMMENT', 'WHITESPACE', 'UNKNOWN', 'ANNOTATION'
])


def tokenize_java(source_code: str) -> List[Token]:
    """
    Tokenize Java source code into a list of Token objects.

    Comments, whitespace, annotations, and unknown characters are discarded.

    Args:
        source_code: The Java source code string.

    Returns:
        List of Token objects with type, value, line, and column.

    Raises:
        TypeError: If source_code is not a string.
    """
    if not isinstance(source_code, str):
        raise TypeError(f"Expected string input, got {type(source_code).__name__}")

    if not source_code.strip():
        return []

    tokens = []
    line_num = 1
    line_start = 0

    for match in _JAVA_MASTER_PATTERN.finditer(source_code):
        token_type = match.lastgroup
        token_value = match.group()
        token_start = match.start()

        # Calculate line and column
        newlines_before = source_code[line_start:token_start].count('\n')
        if newlines_before > 0:
            line_num += newlines_before
            line_start = source_code.rfind('\n', line_start, token_start) + 1

        column = token_start - line_start + 1

        # Update line count for multi-line tokens (block comments, strings)
        newlines_in_token = token_value.count('\n')

        # Skip discarded token types
        if token_type in _JAVA_DISCARD_TYPES:
            if newlines_in_token > 0:
                line_num += newlines_in_token
                line_start = source_code.rfind('\n', token_start, match.end()) + 1
            continue

        # Classify identifiers as KEYWORD, DATATYPE, or IDENTIFIER
        if token_type == 'IDENTIFIER':
            if token_value in JAVA_DATATYPES:
                token_type = 'DATATYPE'
            elif token_value in JAVA_KEYWORDS:
                token_type = 'KEYWORD'
            # else stays IDENTIFIER

        tokens.append(Token(
            type=token_type,
            value=token_value,
            line=line_num,
            column=column
        ))

        if newlines_in_token > 0:
            line_num += newlines_in_token
            line_start = source_code.rfind('\n', token_start, match.end()) + 1

    return tokens


def tokenize_java_file(filepath: str) -> List[Token]:
    """
    Read a Java file and tokenize its contents.

    Args:
        filepath: Path to the .java file.

    Returns:
        List of Token objects.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        IOError: If the file can't be read.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            source_code = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except IOError as e:
        raise IOError(f"Error reading file {filepath}: {e}")

    return tokenize_java(source_code)
