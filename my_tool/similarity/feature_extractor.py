"""
Feature Extractor Module

Extracts per-variable feature vectors from C++ token streams.
Used by StructuralDetector.

Each variable gets a feature vector of 26 integer counts capturing its
usage patterns (in loops, conditions, operations, etc.).
"""

from typing import Dict, List, NamedTuple

from my_tool.tokenizer import Token


class VariableFeatures(NamedTuple):
    """Feature vector for a single variable (26-element profile)."""
    name: str
    features: List[int]  # 26-element feature vector


# Feature indices (matching VariableName.ToArray() order)
F_USED = 0
F_ADDED_OR_SUBTRACTED = 1
F_MULTIPLIED_OR_DIVIDED = 2
F_INVOKED_AS_PARAMETER = 3
F_IN_IF_STATEMENT = 4
F_ARRAY_SUBSCRIPT = 5
F_DEFINED = 6
F_DEFINED_BY_ADD_SUB = 7
F_DEFINED_BY_MUL_DIV = 8
F_DEFINED_BY_EXPR_CONST = 9
F_DEFINED_BY_STRING = 10
F_DEFINED_BY_CHAR = 11
F_DEFINED_BY_NULL = 12
F_DEFINED_BY_BOOL = 13
F_DEFINED_BY_NUMERIC = 14
F_DEFINED_BY_OTHER_VAR = 15
F_ASSIGNED_BY_EXPR_LITERAL = 16
F_ASSIGNED_BY_ADD_SUB = 17
F_ASSIGNED_BY_MUL_DIV = 18
F_ASSIGNED_BY_OTHER_VAR = 19
F_IN_THIRD_LEVEL_LOOP = 20
F_IN_SECOND_LEVEL_LOOP = 21
F_IN_FIRST_LEVEL_LOOP = 22
F_DEFINED_BY_TYPE = 23
F_IN_CASE_STATEMENT = 24
F_IN_SWITCH_STATEMENT = 25

NUM_FEATURES = 26

# Type encoding (matching SyntaxTreeParser.PopulateDeclaration)
TYPE_ENCODING = {
    'int': 1, 'float': 2, 'double': 3, 'string': 4, 'char': 5,
    'auto': 6, 'bool': 7, 'void': 0, 'long': 1, 'short': 1,
    'unsigned': 1, 'signed': 1,
}

# Tokens that indicate a data type for variable declaration
DECL_TYPES = frozenset([
    'int', 'float', 'double', 'char', 'bool', 'void', 'long', 'short',
    'signed', 'unsigned', 'auto', 'string', 'vector', 'map', 'set',
    'list', 'deque', 'array', 'wchar_t',
])

ADD_SUB_OPS = frozenset(['+', '-', '+=', '-='])
MUL_DIV_OPS = frozenset(['*', '/', '*=', '/=', '%', '%='])
ASSIGN_OPS = frozenset(['=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>='])


def extract_features(tokens: List[Token]) -> List[VariableFeatures]:
    """
    Extract per-variable feature vectors from a method's token stream.

    Analyzes the token stream to identify variable declarations and usages,
    building a 26-feature profile for each variable.

    Used by StructuralDetector.

    Args:
        tokens: Token list for a single method.

    Returns:
        List of VariableFeatures, one per variable found.
    """
    if not tokens:
        return []

    variables: Dict[str, List[int]] = {}

    # Pass 0: register function parameters from the signature
    _find_parameters(tokens, variables)

    # Pass 1: identify variable declarations in the body
    _find_declarations(tokens, variables)

    # Pass 2: analyze variable usage patterns
    _analyze_usage(tokens, variables)

    result = []
    for name, feats in variables.items():
        result.append(VariableFeatures(name=name, features=list(feats)))

    return result


def _find_parameters(tokens: List[Token], variables: Dict[str, List[int]]) -> None:
    """
    Extract function parameters from the signature and register them as
    declared variables.

    Scans the token range between the first LPAREN and its matching RPAREN
    (the parameter list), detecting  TYPE IDENTIFIER  pairs (with optional
    array markers) and adding each to *variables* with F_DEFINED set.
    """
    size = len(tokens)

    # Locate the opening brace of the function body (first LBRACE)
    body_start = -1
    for idx in range(size):
        if tokens[idx].type == 'LBRACE':
            body_start = idx
            break
    if body_start < 0:
        return

    # Locate the RPAREN immediately before the body brace
    # (work backwards from body_start to find the matching parameter RPAREN)
    rparen_idx = -1
    for idx in range(body_start - 1, -1, -1):
        t = tokens[idx]
        if t.type == 'RPAREN':
            rparen_idx = idx
            break
        # Stop early if we see something that cannot appear between ) and {
        if t.type in ('LBRACE', 'SEMICOLON'):
            break
    if rparen_idx < 0:
        return

    # Find the matching LPAREN for that RPAREN
    lparen_idx = -1
    depth = 0
    for idx in range(rparen_idx, -1, -1):
        if tokens[idx].type == 'RPAREN':
            depth += 1
        elif tokens[idx].type == 'LPAREN':
            depth -= 1
            if depth == 0:
                lparen_idx = idx
                break
    if lparen_idx < 0:
        return

    # Parse  TYPE IDENTIFIER  pairs inside the parameter list
    i = lparen_idx + 1
    while i < rparen_idx:
        tok = tokens[i]
        if tok.type == 'COMMA':
            i += 1
            continue

        # Match: TYPE IDENTIFIER (optionally followed by [] or qualifiers)
        if (tok.type in ('DATATYPE', 'IDENTIFIER', 'KEYWORD') and
                i + 1 < rparen_idx and
                tokens[i + 1].type == 'IDENTIFIER'):
            var_name = tokens[i + 1].value
            type_val = tok.value

            if var_name not in variables:
                variables[var_name] = [0] * NUM_FEATURES

            variables[var_name][F_DEFINED] += 1
            variables[var_name][F_DEFINED_BY_TYPE] = TYPE_ENCODING.get(type_val, 0)
            i += 2
            # Skip array markers:  int arr[]  or pointer markers
            while i < rparen_idx and tokens[i].type in (
                    'LBRACKET', 'RBRACKET', 'OPERATOR', 'NUMERIC'):
                i += 1
        else:
            i += 1


def _find_declarations(tokens: List[Token], variables: Dict[str, List[int]]) -> None:
    """Find variable declarations in the token stream."""
    size = len(tokens)

    for i in range(size):
        tok = tokens[i]

        # Pattern: TYPE IDENTIFIER [=...] ;
        # or: TYPE IDENTIFIER ,
        if (tok.type == 'DATATYPE' and tok.value in DECL_TYPES and
                i + 1 < size and tokens[i + 1].type == 'IDENTIFIER'):

            var_name = tokens[i + 1].value
            type_val = tok.value

            if var_name not in variables:
                variables[var_name] = [0] * NUM_FEATURES

            variables[var_name][F_DEFINED] += 1
            variables[var_name][F_DEFINED_BY_TYPE] = TYPE_ENCODING.get(type_val, 0)

            # Check what it's defined by (look at initializer if present)
            if i + 2 < size and tokens[i + 2].type == 'OPERATOR' and tokens[i + 2].value == '=':
                _analyze_initializer(tokens, i + 3, var_name, variables)

        # Also catch for-loop declarations: for(int i = ...)
        if (tok.type == 'KEYWORD' and tok.value == 'for' and
                i + 1 < size and tokens[i + 1].type == 'LPAREN' and
                i + 2 < size and tokens[i + 2].type == 'DATATYPE' and
                i + 3 < size and tokens[i + 3].type == 'IDENTIFIER'):

            var_name = tokens[i + 3].value
            type_val = tokens[i + 2].value

            if var_name not in variables:
                variables[var_name] = [0] * NUM_FEATURES

            variables[var_name][F_DEFINED] += 1
            variables[var_name][F_DEFINED_BY_TYPE] = TYPE_ENCODING.get(type_val, 0)


def _analyze_initializer(tokens: List[Token], start: int, var_name: str,
                         variables: Dict[str, List[int]]) -> None:
    """Analyze what a variable is initialized with."""
    size = len(tokens)
    if start >= size:
        return

    feats = variables[var_name]
    # Look at tokens up to next semicolon or comma
    has_add_sub = False
    has_mul_div = False
    has_string = False
    has_char = False
    has_numeric = False
    has_bool = False
    has_null = False
    has_other_var = False
    has_const_expr = False

    j = start
    while j < size and tokens[j].type not in ('SEMICOLON', 'COMMA'):
        t = tokens[j]
        if t.type == 'OPERATOR':
            if t.value in ('+', '-'):
                has_add_sub = True
            elif t.value in ('*', '/'):
                has_mul_div = True
        elif t.type == 'STRING':
            has_string = True
            has_const_expr = True
        elif t.type == 'CHAR':
            has_char = True
            has_const_expr = True
        elif t.type == 'NUMERIC':
            has_numeric = True
            has_const_expr = True
        elif t.type == 'KEYWORD':
            if t.value in ('true', 'false'):
                has_bool = True
                has_const_expr = True
            elif t.value == 'nullptr' or t.value == 'NULL':
                has_null = True
        elif t.type == 'IDENTIFIER':
            has_other_var = True
        j += 1

    if has_add_sub:
        feats[F_DEFINED_BY_ADD_SUB] += 1
    if has_mul_div:
        feats[F_DEFINED_BY_MUL_DIV] += 1
    if has_string:
        feats[F_DEFINED_BY_STRING] += 1
    if has_char:
        feats[F_DEFINED_BY_CHAR] += 1
    if has_numeric:
        feats[F_DEFINED_BY_NUMERIC] += 1
    if has_bool:
        feats[F_DEFINED_BY_BOOL] += 1
    if has_null:
        feats[F_DEFINED_BY_NULL] += 1
    if has_other_var:
        feats[F_DEFINED_BY_OTHER_VAR] += 1
    if has_const_expr:
        feats[F_DEFINED_BY_EXPR_CONST] += 1


def _analyze_usage(tokens: List[Token], variables: Dict[str, List[int]]) -> None:
    """
    Analyze how variables are used throughout the method.

    Brace-stack tracking
    --------------------
    The depth of loop/if/switch nesting is updated when an LBRACE is seen
    (not when the keyword is seen).  A *pending_context* variable records
    the most recent control-flow keyword and is consumed by the next LBRACE.
    If a semicolon is encountered at paren-depth 0 (i.e., outside a for(;;)
    header) with a pending keyword, the keyword was for a brace-less body;
    pending_context is cleared without incrementing any depth counter.
    This prevents brace-less  for/while  bodies from permanently inflating
    loop_depth (the original bug).
    """
    size = len(tokens)

    # Nesting depths (updated on LBRACE, decremented on matching RBRACE)
    loop_depth = 0
    if_depth = 0
    switch_depth = 0
    case_depth = 0

    # Stack of context labels pushed when a control-flow LBRACE is entered
    brace_stack: List[str] = []

    # Keyword seen but not yet paired with its LBRACE
    pending_context: str = ''

    # Paren depth – used to distinguish semicolons inside  for(;;)  from
    # the statement-terminating semicolon of a brace-less body
    paren_depth: int = 0

    for i in range(size):
        tok = tokens[i]

        # ── Parenthesis depth tracking ──────────────────────────────────────
        if tok.type == 'LPAREN':
            paren_depth += 1
        elif tok.type == 'RPAREN':
            paren_depth = max(0, paren_depth - 1)

        # ── Keyword recognition (set pending_context, handle case/default) ──
        elif tok.type == 'KEYWORD':
            if tok.value in ('for', 'while', 'do'):
                pending_context = 'loop'
            elif tok.value == 'if':
                pending_context = 'if'
            elif tok.value == 'switch':
                pending_context = 'switch'
            elif tok.value == 'case':
                case_depth += 1
            elif tok.value == 'default' and switch_depth > 0:
                case_depth += 1

        # ── LBRACE: open a new nesting level ────────────────────────────────
        elif tok.type == 'LBRACE':
            ctx = pending_context if pending_context else 'other'
            brace_stack.append(ctx)
            if ctx == 'loop':
                loop_depth += 1
            elif ctx == 'if':
                if_depth += 1
            elif ctx == 'switch':
                switch_depth += 1
            pending_context = ''  # consumed

        # ── SEMICOLON outside parens: brace-less single-statement body ──────
        elif tok.type == 'SEMICOLON' and paren_depth == 0:
            # A semicolon at paren-depth 0 ends a statement.  If there is
            # a pending control-flow keyword it means the body was brace-less
            # (e.g.  for(...) arr[i]=0; ).  Clear without touching depths.
            pending_context = ''

        # ── RBRACE: close the matching nesting level ─────────────────────────
        elif tok.type == 'RBRACE':
            if brace_stack:
                context = brace_stack.pop()
                if context == 'loop':
                    loop_depth = max(0, loop_depth - 1)
                elif context == 'if':
                    if_depth = max(0, if_depth - 1)
                elif context == 'switch':
                    switch_depth = max(0, switch_depth - 1)
                    case_depth = 0
            pending_context = ''

        # Analyze variable usage
        if tok.type == 'IDENTIFIER' and tok.value in variables:
            feats = variables[tok.value]
            feats[F_USED] += 1

            # Check context: in if statement
            if if_depth > 0:
                feats[F_IN_IF_STATEMENT] += 1

            # Check context: in switch/case
            if switch_depth > 0:
                feats[F_IN_SWITCH_STATEMENT] += 1
            if case_depth > 0:
                feats[F_IN_CASE_STATEMENT] += 1

            # Check context: loop depth
            if loop_depth >= 3:
                feats[F_IN_THIRD_LEVEL_LOOP] += 1
            elif loop_depth == 2:
                feats[F_IN_SECOND_LEVEL_LOOP] += 1
            elif loop_depth == 1:
                feats[F_IN_FIRST_LEVEL_LOOP] += 1

            # Check if used as array subscript: identifier[...]
            if i + 1 < size and tokens[i + 1].type == 'LBRACKET':
                feats[F_ARRAY_SUBSCRIPT] += 1

            # Check if invoked as parameter: ...( identifier, ...)
            if (i > 0 and tokens[i - 1].type in ('LPAREN', 'COMMA') and
                    i + 1 < size and tokens[i + 1].type in ('RPAREN', 'COMMA')):
                feats[F_INVOKED_AS_PARAMETER] += 1

            # Check if in add/sub operation
            if (i > 0 and tokens[i - 1].type == 'OPERATOR' and
                    tokens[i - 1].value in ADD_SUB_OPS):
                feats[F_ADDED_OR_SUBTRACTED] += 1
            elif (i + 1 < size and tokens[i + 1].type == 'OPERATOR' and
                  tokens[i + 1].value in ADD_SUB_OPS):
                feats[F_ADDED_OR_SUBTRACTED] += 1

            # Check if in mul/div operation
            if (i > 0 and tokens[i - 1].type == 'OPERATOR' and
                    tokens[i - 1].value in MUL_DIV_OPS):
                feats[F_MULTIPLIED_OR_DIVIDED] += 1
            elif (i + 1 < size and tokens[i + 1].type == 'OPERATOR' and
                  tokens[i + 1].value in MUL_DIV_OPS):
                feats[F_MULTIPLIED_OR_DIVIDED] += 1

            # Check if being assigned (var = ...)
            if (i + 1 < size and tokens[i + 1].type == 'OPERATOR' and
                    tokens[i + 1].value in ASSIGN_OPS):
                # Look at right side of assignment
                _analyze_assignment_rhs(tokens, i + 2, feats)


def _analyze_assignment_rhs(tokens: List[Token], start: int,
                            feats: List[int]) -> None:
    """Analyze right-hand side of an assignment."""
    size = len(tokens)
    if start >= size:
        return

    j = start
    has_literal = False
    has_add_sub = False
    has_mul_div = False
    has_other_var = False

    while j < size and tokens[j].type not in ('SEMICOLON',):
        t = tokens[j]
        if t.type == 'OPERATOR':
            if t.value in ('+', '-'):
                has_add_sub = True
            elif t.value in ('*', '/'):
                has_mul_div = True
        elif t.type in ('NUMERIC', 'STRING', 'CHAR'):
            has_literal = True
        elif t.type == 'KEYWORD' and t.value in ('true', 'false', 'nullptr', 'NULL'):
            has_literal = True
        elif t.type == 'IDENTIFIER':
            has_other_var = True
        j += 1

    if has_literal:
        feats[F_ASSIGNED_BY_EXPR_LITERAL] += 1
    if has_add_sub:
        feats[F_ASSIGNED_BY_ADD_SUB] += 1
    if has_mul_div:
        feats[F_ASSIGNED_BY_MUL_DIV] += 1
    if has_other_var:
        feats[F_ASSIGNED_BY_OTHER_VAR] += 1
