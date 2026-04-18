"""
C# Tokenizer Module

Tokenizes C# source code into a stream of categorized tokens,
discarding comments, whitespace, and preprocessor directives.

Output format matches the C++ tokenizer (Token NamedTuple) so that
the downstream normalizer and detectors work without modification.
"""

import re
from typing import List

from my_tool.tokenizer import Token


# C# keywords (excluding types listed in CS_DATATYPES)
CS_KEYWORDS = frozenset([
    'abstract', 'as', 'base', 'break', 'case', 'catch', 'class', 'const',
    'continue', 'default', 'delegate', 'do', 'else', 'enum', 'event',
    'explicit', 'extern', 'false', 'finally', 'fixed', 'for', 'foreach',
    'goto', 'if', 'implicit', 'in', 'interface', 'internal', 'is', 'lock',
    'namespace', 'new', 'null', 'operator', 'out', 'override', 'params',
    'private', 'protected', 'public', 'readonly', 'ref', 'return', 'sealed',
    'sizeof', 'stackalloc', 'static', 'struct', 'switch', 'this', 'throw',
    'true', 'try', 'typeof', 'unchecked', 'unsafe', 'using', 'virtual',
    'volatile', 'while', 'record', 'async', 'await', 'yield', 'get', 'set',
    'init', 'value', 'where'
])

# C# data types
CS_DATATYPES = frozenset([
    'bool', 'byte', 'sbyte', 'char', 'decimal', 'double', 'float', 'int', 'uint',
    'nint', 'nuint', 'long', 'ulong', 'short', 'ushort', 'object', 'string', 'dynamic',
    'void', 'var', 'Task', 'ValueTask', 'List', 'IEnumerable', 'ICollection', 'IList',
    'Dictionary', 'IDictionary', 'HashSet', 'ISet', 'Span', 'ReadOnlySpan', 'Memory',
    'ReadOnlyMemory', 'Func', 'Action', 'Predicate', 'Tuple', 'Guid', 'DateTime', 'TimeSpan'
])

# Token patterns (order matters — first match wins)
_CS_TOKEN_PATTERNS = [
    # Multi-line comments
    ('BLOCK_COMMENT', r'/\*[\s\S]*?\*/'),
    # Single-line comments
    ('LINE_COMMENT', r'//[^\n]*'),
    # Preprocessor directives
    ('PREPROCESSOR', r'#\s*\w+[^\n]*'),
    # String literals (handles @"" and $"" loosely)
    ('STRING', r'@?"(?:[^"\\]|\\.)*"'),
    # Interpolated strings briefly:
    ('INTERP_STRING', r'\$@?"(?:[^"\\]|\\.)*"'),
    # Character literals
    ('CHAR', r"'(?:[^'\\]|\\.)*'"),
    # Numeric literals
    ('NUMERIC', r'0[xX][0-9a-fA-F_]+[uUlL]*'
               r'|0[bB][01_]+[uUlL]*'
               r'|[0-9_]+\.[0-9_]*(?:[eE][+-]?[0-9_]+)?[fFdDmM]?'
               r'|\.[0-9_]+(?:[eE][+-]?[0-9_]+)?[fFdDmM]?'
               r'|[0-9_]+[eE][+-]?[0-9_]+[fFdDmM]?'
               r'|[0-9_]+[fFdDmMuUlL]*'),
    # Identifiers
    ('IDENTIFIER', r'[a-zA-Z_]\w*'),
    # Multi-character operators
    ('OPERATOR', r'<<='
               r'|>>='
               r'|>>>='
               r'|<<|>>>|>>'
               r'|\+\+|--|->|=>'
               r'|&&|\|\||::'
               r'|\?\?=|\?\?'
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
    # Whitespace 
    ('WHITESPACE', r'\s+'),
    # Anything else
    ('UNKNOWN', r'.'),
]

# Compile the master regex
_CS_MASTER_PATTERN = re.compile(
    '|'.join(f'(?P<{name}>{pattern})' for name, pattern in _CS_TOKEN_PATTERNS),
    re.DOTALL
)

# Token types to discard
_CS_DISCARD_TYPES = frozenset([
    'BLOCK_COMMENT', 'LINE_COMMENT', 'WHITESPACE', 'UNKNOWN', 'PREPROCESSOR'
])


def tokenize_cs(source_code: str) -> List[Token]:
    """
    Tokenize C# source code into a list of Token objects.
    """
    if not isinstance(source_code, str):
        raise TypeError(f"Expected string input, got {type(source_code).__name__}")

    if not source_code.strip():
        return []

    tokens = []
    line_num = 1
    line_start = 0

    for match in _CS_MASTER_PATTERN.finditer(source_code):
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

        # Treat INTERP_STRING as STRING
        if token_type == 'INTERP_STRING':
            token_type = 'STRING'

        # Skip discarded token types
        if token_type in _CS_DISCARD_TYPES:
            if newlines_in_token > 0:
                line_num += newlines_in_token
                line_start = source_code.rfind('\n', token_start, match.end()) + 1
            continue

        # Classify identifiers
        if token_type == 'IDENTIFIER':
            if token_value in CS_DATATYPES:
                token_type = 'DATATYPE'
            elif token_value in CS_KEYWORDS:
                token_type = 'KEYWORD'

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


def tokenize_cs_file(filepath: str) -> List[Token]:
    """
    Read a C# file and tokenize its contents.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            source_code = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except IOError as e:
        raise IOError(f"Error reading file {filepath}: {e}")

    return tokenize_cs(source_code)
