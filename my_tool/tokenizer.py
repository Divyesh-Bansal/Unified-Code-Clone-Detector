"""
C++ Tokenizer Module

Tokenizes C++ source code into a stream of categorized tokens,
discarding comments and whitespace.
"""

import re
from typing import List, NamedTuple


class Token(NamedTuple):
    """Represents a single token from C++ source code."""
    type: str       # Token category (KEYWORD, IDENTIFIER, NUMERIC, etc.)
    value: str      # The actual text of the token
    line: int       # Line number (1-indexed)
    column: int     # Column number (1-indexed)


# C++ keywords
CPP_KEYWORDS = frozenset([
    'alignas', 'alignof', 'and', 'and_eq', 'asm', 'auto', 'bitand', 'bitor',
    'bool', 'break', 'case', 'catch', 'char', 'char8_t', 'char16_t', 'char32_t',
    'class', 'compl', 'concept', 'const', 'consteval', 'constexpr', 'constinit',
    'const_cast', 'continue', 'co_await', 'co_return', 'co_yield', 'decltype',
    'default', 'delete', 'do', 'double', 'dynamic_cast', 'else', 'enum',
    'explicit', 'export', 'extern', 'false', 'float', 'for', 'friend', 'goto',
    'if', 'inline', 'int', 'long', 'mutable', 'namespace', 'new', 'noexcept',
    'not', 'not_eq', 'nullptr', 'operator', 'or', 'or_eq', 'private',
    'protected', 'public', 'register', 'reinterpret_cast', 'requires', 'return',
    'short', 'signed', 'sizeof', 'static', 'static_assert', 'static_cast',
    'struct', 'switch', 'template', 'this', 'thread_local', 'throw', 'true',
    'try', 'typedef', 'typeid', 'typename', 'union', 'unsigned', 'using',
    'virtual', 'void', 'volatile', 'wchar_t', 'while', 'xor', 'xor_eq',
    'string', 'vector', 'map', 'set', 'list', 'deque', 'array',
    'cout', 'cin', 'endl', 'std', 'printf', 'scanf', 'puts', 'gets',
    'include', 'define', 'ifdef', 'ifndef', 'endif', 'pragma',
])

# C++ data types (subset of keywords used for method detection)
CPP_DATATYPES = frozenset([
    'void', 'int', 'char', 'float', 'double', 'bool', 'long', 'short',
    'signed', 'unsigned', 'auto', 'wchar_t', 'char8_t', 'char16_t', 'char32_t',
    'string', 'vector', 'map', 'set', 'list', 'deque', 'array',
])

# Token patterns (order matters — first match wins)
_TOKEN_PATTERNS = [
    # Multi-line comments
    ('BLOCK_COMMENT', r'/\*[\s\S]*?\*/'),
    # Single-line comments
    ('LINE_COMMENT', r'//[^\n]*'),
    # Preprocessor directives
    ('PREPROCESSOR', r'#\s*\w+[^\n]*'),
    # String literals (handles escaped quotes)
    ('STRING', r'"(?:[^"\\]|\\.)*"'),
    # Character literals
    ('CHAR', r"'(?:[^'\\]|\\.)*'"),
    # Numeric literals (hex, float, int)
    ('NUMERIC', r'0[xX][0-9a-fA-F]+(?:u|U|l|L|ll|LL|ull|ULL)?'
               r'|[0-9]+\.[0-9]*(?:[eE][+-]?[0-9]+)?[fFlL]?'
               r'|\.[0-9]+(?:[eE][+-]?[0-9]+)?[fFlL]?'
               r'|[0-9]+[eE][+-]?[0-9]+[fFlL]?'
               r'|[0-9]+(?:u|U|l|L|ll|LL|ull|ULL)?'),
    # Identifiers (and keywords — distinguished later)
    ('IDENTIFIER', r'[a-zA-Z_]\w*'),
    # Multi-character operators
    ('OPERATOR', r'<<='
               r'|>>='
               r'|<<|>>'
               r'|\+\+|--|->|\.\.\.'
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
_MASTER_PATTERN = re.compile(
    '|'.join(f'(?P<{name}>{pattern})' for name, pattern in _TOKEN_PATTERNS),
    re.DOTALL
)

# Token types to discard (comments, whitespace, preprocessor, unknown)
_DISCARD_TYPES = frozenset([
    'BLOCK_COMMENT', 'LINE_COMMENT', 'WHITESPACE', 'UNKNOWN', 'PREPROCESSOR'
])


def tokenize(source_code: str) -> List[Token]:
    """
    Tokenize C++ source code into a list of Token objects.

    Comments, whitespace, preprocessor directives, and unknown characters
    are discarded.

    Args:
        source_code: The C++ source code string.

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

    for match in _MASTER_PATTERN.finditer(source_code):
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
        if token_type in _DISCARD_TYPES:
            if newlines_in_token > 0:
                line_num += newlines_in_token
                line_start = source_code.rfind('\n', token_start, match.end()) + 1
            continue

        # Classify identifiers as KEYWORD, DATATYPE, or IDENTIFIER
        if token_type == 'IDENTIFIER':
            if token_value in CPP_DATATYPES:
                token_type = 'DATATYPE'
            elif token_value in CPP_KEYWORDS:
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


def tokenize_file(filepath: str) -> List[Token]:
    """
    Read a C++ file and tokenize its contents.

    Args:
        filepath: Path to the .cpp or .h file.

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

    return tokenize(source_code)
