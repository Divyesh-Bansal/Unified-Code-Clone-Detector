"""
Variable Normalizer Module

Renames all identifiers in a token stream to generic names (id0, id1, id2...),
ensuring structurally identical code with different variable names produces
identical token streams for LexicalDetector comparison.
"""

from typing import Dict, List, Tuple

from my_tool.tokenizer import Token


def normalize(tokens: List[Token]) -> Tuple[List[Token], Dict[str, str]]:
    """
    Normalize identifiers in a token list by replacing them with
    sequential generic names (id0, id1, id2, ...).

    Only tokens of type 'IDENTIFIER' are renamed. Keywords, data types,
    operators, etc. are left unchanged.

    Args:
        tokens: List of Token objects from the tokenizer.

    Returns:
        A tuple of:
        - List of new Token objects with normalized identifiers
        - Dictionary mapping original names to normalized names

    Raises:
        TypeError: If tokens is not a list.
    """
    if not isinstance(tokens, list):
        raise TypeError(f"Expected list of tokens, got {type(tokens).__name__}")

    dictionary: Dict[str, str] = {}
    counter = 0
    normalized_tokens: List[Token] = []

    for token in tokens:
        if token.type == 'IDENTIFIER':
            original_name = token.value
            if original_name not in dictionary:
                dictionary[original_name] = f"id{counter}"
                counter += 1
            # Create a new token with the normalized name
            normalized_tokens.append(Token(
                type=token.type,
                value=dictionary[original_name],
                line=token.line,
                column=token.column
            ))
        else:
            normalized_tokens.append(token)

    return normalized_tokens, dictionary
