"""
Feature Extractor Module

Extracts per-variable feature vectors from C++, Java, and C# token streams.
Used by StructuralDetector.

Each variable gets a feature vector of 27 integer counts capturing its
usage patterns (in loops, conditions, operations, OOP method calls, etc.).

Language support
----------------
* C++  — full support (original)
* Java — types mapped via UNIFIED_TYPE_ENCODING; OOP method calls detected
* C#   — types mapped via UNIFIED_TYPE_ENCODING; OOP method calls detected
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
F_INVOKED_METHOD_ON   = 26  # var.method() — variable invokes a method on itself

NUM_FEATURES = 27

# Unified language-agnostic type encoding
# Maps semantically equivalent types across C++, Java, and C# to the same
# integer so that cross-language feature vectors are directly comparable.
#
# Code  Semantic group
# ----  -----------------------------------------------------------------
#  0    void / no type
#  1    integer  (int, long, short, byte, uint, …)
#  2    float
#  3    double / decimal
#  4    string / text  (string, String, wchar_t, …)
#  5    char / Character
#  6    type-inferred  (auto, var, dynamic)
#  7    boolean  (bool, boolean, Boolean)
#  8    list / array container  (vector, List, ArrayList, …)
#  9    map / dictionary  (map, HashMap, Dictionary, …)
# 10    set  (set, HashSet, TreeSet, ISet, …)
UNIFIED_TYPE_ENCODING = {
    # void
    'void':         0,
    # integers — C++
    'int':          1, 'long':     1, 'short':   1,
    'signed':       1, 'unsigned': 1,
    # integers — Java
    'byte':         1, 'Integer':  1, 'Long':    1, 'Short':   1, 'Byte': 1,
    # integers — C#
    'uint':         1, 'ulong':    1, 'ushort':  1, 'sbyte':   1,
    'nint':         1, 'nuint':    1,
    # float
    'float':        2, 'Float':    2,
    # double / decimal
    'double':       3, 'Double':   3, 'decimal':  3,
    # string / text
    'string':       4, 'String':   4, 'wchar_t': 4,
    'char8_t':      4, 'char16_t': 4,
    # char
    'char':         5, 'Character': 5,
    # type-inferred
    'auto':         6, 'var':      6, 'dynamic': 6,
    # boolean
    'bool':         7, 'boolean':  7, 'Boolean': 7,
    # list / array containers
    'vector':       8, 'list':     8, 'deque':   8, 'array':   8,
    'List':         8, 'ArrayList': 8, 'LinkedList': 8,
    'IList':        8, 'ICollection': 8, 'IEnumerable': 8,
    'Stack':        8, 'Queue':    8, 'Deque':   8, 'Vector':  8,
    'Collection':   8,
    # map / dictionary
    'map':          9, 'Map':      9, 'HashMap': 9, 'TreeMap': 9,
    'LinkedHashMap': 9, 'Dictionary': 9, 'IDictionary': 9,
    # set
    'set':         10, 'Set':     10, 'HashSet': 10,
    'TreeSet':     10, 'ISet':    10,
}

# Backward-compatible alias — external code importing TYPE_ENCODING still works
TYPE_ENCODING = UNIFIED_TYPE_ENCODING

# Tokens that indicate a data type for variable declaration.
# Extended to include Java and C# type names so that _find_declarations()
# works correctly regardless of which tokenizer produced the token stream.
DECL_TYPES = frozenset([
    # C++ primitives and standard-library types
    'int', 'float', 'double', 'char', 'bool', 'void', 'long', 'short',
    'signed', 'unsigned', 'auto', 'string', 'vector', 'map', 'set',
    'list', 'deque', 'array', 'wchar_t', 'char8_t', 'char16_t',
    # Java primitives and boxed / common library types
    'boolean', 'byte', 'Integer', 'Long', 'Float', 'Double',
    'Boolean', 'Byte', 'Short', 'Character', 'String', 'Object',
    'List', 'ArrayList', 'LinkedList', 'Map', 'HashMap', 'TreeMap',
    'Set', 'HashSet', 'Queue', 'Deque', 'Stack', 'Vector', 'Collection',
    # C# primitives and collection types
    'decimal', 'uint', 'ulong', 'ushort', 'sbyte', 'nint', 'nuint',
    'var', 'dynamic', 'Dictionary', 'IDictionary', 'IList', 'ICollection',
    'IEnumerable', 'ISet',
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


def _skip_template_args(tokens: List[Token], start: int, size: int) -> int:
    """
    If tokens[start] opens a template/generic argument list (i.e. is an
    OPERATOR with value '<'), skip forward past the matching closing '>' and
    return the index of the first token *after* the closing '>'.

    Handles nested templates such as ``Map<String, List<Integer>>``.

    If tokens[start] is not '<', returns *start* unchanged.
    """
    if start >= size or not (tokens[start].type == 'OPERATOR' and tokens[start].value == '<'):
        return start

    depth = 0
    j = start
    while j < size:
        t = tokens[j]
        if t.type == 'OPERATOR':
            if t.value == '<':
                depth += 1
            elif t.value == '>':
                depth -= 1
                if depth == 0:
                    return j + 1
            elif t.value == '>>':
                # C++ tokeniser may produce '>>' for closing nested templates
                depth -= 2
                if depth <= 0:
                    return j + 1
        j += 1
    # Unmatched '<' — bail out to the original position
    return start


def _find_declarations(tokens: List[Token], variables: Dict[str, List[int]]) -> None:
    """Find variable declarations in the token stream.

    Handles plain types (``int x``) as well as template/generic types
    (``vector<int> obj``, ``List<String> items``, ``Map<K, V> m``).
    """
    size = len(tokens)

    for i in range(size):
        tok = tokens[i]

        # Pattern: TYPE [<TemplateArgs>] IDENTIFIER [=...] ;
        if tok.type == 'DATATYPE' and tok.value in DECL_TYPES:
            # Skip over template/generic arguments if present
            next_idx = _skip_template_args(tokens, i + 1, size)

            if next_idx < size and tokens[next_idx].type == 'IDENTIFIER':
                var_name = tokens[next_idx].value
                type_val = tok.value

                if var_name not in variables:
                    variables[var_name] = [0] * NUM_FEATURES

                variables[var_name][F_DEFINED] += 1
                variables[var_name][F_DEFINED_BY_TYPE] = UNIFIED_TYPE_ENCODING.get(type_val, 0)

                # Check what it's defined by (look at initializer if present)
                init_idx = next_idx + 1
                if (init_idx < size
                        and tokens[init_idx].type == 'OPERATOR'
                        and tokens[init_idx].value == '='):
                    _analyze_initializer(tokens, init_idx + 1, var_name, variables)

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

            # Check if variable invokes a method on itself: var.method(
            # Pattern: IDENTIFIER  DOT  IDENTIFIER  LPAREN
            if (i + 3 < size
                    and tokens[i + 1].type == 'DOT'
                    and tokens[i + 2].type == 'IDENTIFIER'
                    and tokens[i + 3].type == 'LPAREN'):
                feats[F_INVOKED_METHOD_ON] += 1

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
