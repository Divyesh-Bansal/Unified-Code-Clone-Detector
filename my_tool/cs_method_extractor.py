"""
C# Method Extractor Module

Extracts method boundaries from a C# token stream using brace-matching.
Handles access modifiers, static/abstract/async keywords, and generic constraints,
avoiding constructors and class definitions.

Reuses the MethodInfo NamedTuple from method_extractor.py.
"""

from typing import List, Optional, Set

from my_tool.tokenizer import Token
from my_tool.method_extractor import MethodInfo


# Keywords that can precede a method's return type in C#
_CS_MODIFIERS = frozenset([
    'public', 'private', 'protected', 'internal', 'static', 'readonly',
    'virtual', 'override', 'sealed', 'abstract', 'extern', 'unsafe', 'async',
    'partial', 'new', 'volatile'
])

# Keywords that indicate a class/interface/enum/struct/record definition
_CLASS_KEYWORDS = frozenset(['class', 'interface', 'enum', 'struct', 'record'])


def _find_class_names(tokens: List[Token]) -> Set[str]:
    """
    Scan tokens to find all class/interface/enum/struct/record names so we can skip
    constructors (methods whose name matches a class name).
    """
    names: Set[str] = set()
    size = len(tokens)
    for i in range(size - 1):
        if (tokens[i].type == 'KEYWORD' and
                tokens[i].value in _CLASS_KEYWORDS and
                tokens[i + 1].type == 'IDENTIFIER'):
            names.add(tokens[i + 1].value)
    return names


def _find_cs_method(tokens: List[Token], start: int,
                      class_names: Set[str]) -> Optional[tuple]:
    """
    Find the next C# method starting from position 'start'.
    """
    min_method_tokens = 6  # Smallest: type name ( ) { }
    size = len(tokens)

    i = start
    while i < size - min_method_tokens + 1:
        tok = tokens[i]

        # Skip modifier keywords
        mod_start = i
        while (i < size and
               tok.type == 'KEYWORD' and
               tok.value in _CS_MODIFIERS):
            i += 1
            if i < size:
                tok = tokens[i]

        if i + 5 > size:
            i = mod_start + 1
            continue

        tok0 = tokens[i]      # Expected: return type
        tok1 = tokens[i + 1]  # Expected: method name
        tok2 = tokens[i + 2]  # Expected: LPAREN

        # Check for pattern: [DATATYPE|IDENTIFIER|KEYWORD] IDENTIFIER LPAREN
        if (tok0.type in ('DATATYPE', 'IDENTIFIER', 'KEYWORD') and
                tok1.type == 'IDENTIFIER' and
                tok2.type == 'LPAREN'):

            return_type = tok0.value
            func_name = tok1.value

            # Skip constructors
            if func_name in class_names:
                i = mod_start + 1
                continue

            # Skip class definitions
            if tok0.value in _CLASS_KEYWORDS:
                i = mod_start + 1
                continue

            # Find matching RPAREN
            j = i + 3
            paren_depth = 1
            param_count = 0
            has_params = False

            while j < size and paren_depth > 0:
                if tokens[j].type == 'LPAREN':
                    paren_depth += 1
                elif tokens[j].type == 'RPAREN':
                    paren_depth -= 1
                elif tokens[j].type == 'COMMA' and paren_depth == 1:
                    param_count += 1
                elif paren_depth == 1 and tokens[j].type not in ('RPAREN',):
                    has_params = True
                j += 1

            if paren_depth != 0:
                i = mod_start + 1
                continue

            if has_params:
                param_count += 1

            rparen_idx = j - 1

            # Check if next token after ) is { (allow 'where XYZ' in between)
            if rparen_idx + 1 >= size:
                i = mod_start + 1
                continue

            brace_idx = rparen_idx + 1
            while (brace_idx < size and
                   tokens[brace_idx].type in ('KEYWORD', 'IDENTIFIER', 'COMMA', 'OPERATOR', 'DOT')):
                brace_idx += 1

            if brace_idx >= size or tokens[brace_idx].type != 'LBRACE':
                i = mod_start + 1
                continue

            # Match braces to find end of method body
            brace_depth = 1
            k = brace_idx + 1
            while k < size and brace_depth > 0:
                if tokens[k].type == 'LBRACE':
                    brace_depth += 1
                elif tokens[k].type == 'RBRACE':
                    brace_depth -= 1
                k += 1

            if brace_depth != 0:
                # Malformed or end of file
                i = mod_start + 1
                continue

            end_idx = k - 1  # Index of closing brace
            return (mod_start, end_idx, func_name, return_type, param_count)

        i = mod_start + 1

    return None


def extract_cs_methods(tokens: List[Token]) -> List[MethodInfo]:
    """
    Extract all methods from a C# token stream.
    """
    if not isinstance(tokens, list):
        raise TypeError(f"Expected list of tokens, got {type(tokens).__name__}")

    if not tokens:
        return []

    class_names = _find_class_names(tokens)
    methods = []
    search_start = 0

    while True:
        result = _find_cs_method(tokens, search_start, class_names)
        if result is None:
            break

        start_idx, end_idx, func_name, return_type, param_count = result
        method_tokens = tokens[start_idx:end_idx + 1]

        start_line = tokens[start_idx].line
        end_line = tokens[end_idx].line

        methods.append(MethodInfo(
            name=func_name,
            tokens=method_tokens,
            start_line=start_line,
            end_line=end_line,
            return_type=return_type,
            param_count=param_count
        ))

        # Continue searching after this method
        search_start = end_idx + 1

    return methods
