"""
Method Extractor Module

Extracts function/method boundaries from a C++ token stream using
brace-matching.
"""

from typing import List, NamedTuple, Optional

from my_tool.tokenizer import Token


class MethodInfo(NamedTuple):
    """Represents an extracted method/function."""
    name: str               # Function name
    tokens: List[Token]     # All tokens belonging to this method
    start_line: int         # Starting line number in source file
    end_line: int           # Ending line number in source file
    return_type: str        # Return type (e.g., "void", "int")
    param_count: int        # Number of parameters


def _find_method(tokens: List[Token], start: int) -> Optional[tuple]:
    """
    Find the next method/function starting from position 'start' in the token list.

    Looks for the pattern: [DataType/Identifier] [Identifier] ( ... ) { ... }
    with balanced brace tracking.

    Args:
        tokens: List of tokens from the tokenizer.
        start: Starting index to search from.

    Returns:
        Tuple of (start_index, end_index, name, return_type, param_count)
        or None if no method is found.
    """
    min_method_tokens = 6  # Smallest possible: type name ( ) { }
    size = len(tokens)

    i = start
    while i < size - min_method_tokens + 1:
        # Look for pattern: [DATATYPE|IDENTIFIER] [IDENTIFIER] [LPAREN]
        tok0 = tokens[i]
        tok1 = tokens[i + 1]
        tok2 = tokens[i + 2]

        if (tok0.type in ('DATATYPE', 'IDENTIFIER', 'KEYWORD') and
                tok1.type == 'IDENTIFIER' and
                tok2.type == 'LPAREN'):

            return_type = tok0.value
            func_name = tok1.value

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
                i += 1
                continue

            if has_params:
                param_count += 1

            rparen_idx = j - 1

            # Check if next token after ) is {
            if rparen_idx + 1 >= size:
                i += 1
                continue

            # Allow 'const', 'override', 'noexcept' etc. between ) and {
            brace_idx = rparen_idx + 1
            while brace_idx < size and tokens[brace_idx].type in ('KEYWORD', 'IDENTIFIER'):
                brace_idx += 1

            if brace_idx >= size or tokens[brace_idx].type != 'LBRACE':
                i += 1
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
                i += 1
                continue

            end_idx = k - 1  # Index of closing brace
            return (i, end_idx, func_name, return_type, param_count)

        i += 1

    return None


def extract_methods(tokens: List[Token]) -> List[MethodInfo]:
    """
    Extract all methods/functions from a C++ token stream.

    Args:
        tokens: List of Token objects from the tokenizer.

    Returns:
        List of MethodInfo objects, one per extracted method.

    Raises:
        TypeError: If tokens is not a list.
    """
    if not isinstance(tokens, list):
        raise TypeError(f"Expected list of tokens, got {type(tokens).__name__}")

    if not tokens:
        return []

    methods = []
    search_start = 0

    while True:
        result = _find_method(tokens, search_start)
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
