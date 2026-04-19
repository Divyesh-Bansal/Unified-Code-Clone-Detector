"""Tests for semantic similarity module — tiered pipeline."""

import pytest
from my_tool.tokenizer import tokenize, Token
from my_tool.similarity.semantic import (
    semantic_similarity,
    _return_type_score,
    _param_count_score,
    _control_flow_score,
    _type_distribution_score,
    _tokens_to_structural_nodes,
    _ngram_jaccard,
    _ast_sequence_score,
    _tier1_score,
    _FAST_PASS_THRESHOLD,
)


# ═══════════════════════════════════════════════════════════════════════
# Tier-1 helpers (existing logic — tests preserved & adapted)
# ═══════════════════════════════════════════════════════════════════════

class TestReturnTypeScore:
    def test_identical(self):
        assert _return_type_score("int", "int") == 100.0

    def test_unknown(self):
        assert _return_type_score("", "int") == 50.0

    def test_same_numeric_group(self):
        assert _return_type_score("int", "float") == 85.0

    def test_different_groups(self):
        assert _return_type_score("int", "vector") == 30.0

    def test_custom_types(self):
        assert _return_type_score("MyClass", "YourClass") == 60.0


class TestParamCountScore:
    def test_equal(self):
        assert _param_count_score(3, 3) == 100.0

    def test_zero_both(self):
        assert _param_count_score(0, 0) == 100.0

    def test_different(self):
        score = _param_count_score(2, 5)
        assert 0 <= score <= 100
        assert score < 100.0


class TestControlFlowScore:
    def test_no_flow_both(self):
        tokens = tokenize("int x = 5;")
        assert _control_flow_score(tokens, tokens) == 100.0

    def test_identical_flow(self):
        code = "if (x) { for (;;) { } }"
        tokens = tokenize(code)
        assert _control_flow_score(tokens, tokens) == 100.0


class TestTypeDistributionScore:
    def test_identical(self):
        tokens = tokenize("int x = 5;")
        score = _type_distribution_score(tokens, tokens)
        assert score > 99.0

    def test_empty(self):
        assert _type_distribution_score([], []) == 100.0


# ═══════════════════════════════════════════════════════════════════════
# Tier-1 aggregate & fast-pass filter
# ═══════════════════════════════════════════════════════════════════════

class TestTier1Score:
    def test_identical_code_high(self):
        code = "int add(int a, int b) { return a + b; }"
        tokens = tokenize(code)
        ts, ps, cf, ds, combined = _tier1_score(
            tokens, tokens, "int", "int", 2, 2)
        assert combined > 80.0

    def test_threshold_exists(self):
        assert _FAST_PASS_THRESHOLD == 30.0


class TestFastPassFilter:
    def test_very_different_code_short_circuits(self):
        """Code with completely different structure should score low and
        the fast-pass should return the tier-1 combined score directly."""
        code_a = "int f(int x) { return x; }"
        # Completely different token structure
        code_b = """
        void g(string a, string b, string c, int d, int e) {
            for (int i = 0; i < 100; i++) {
                for (int j = 0; j < 100; j++) {
                    if (i == j) {
                        while (true) {
                            try { throw; } catch { break; }
                        }
                    }
                }
            }
        }
        """
        tokens_a = tokenize(code_a)
        tokens_b = tokenize(code_b)
        score = semantic_similarity(tokens_a, tokens_b, "int", "void", 1, 5)
        # Should be low — the tier-1 combined score is used directly
        assert score < 50.0


# ═══════════════════════════════════════════════════════════════════════
# Tier-2: Structural pseudo-AST helpers
# ═══════════════════════════════════════════════════════════════════════

class TestTokensToStructuralNodes:
    def test_if_statement(self):
        nodes = _tokens_to_structural_nodes(tokenize("if (x) { }"))
        assert 'IfStmt' in nodes
        assert 'Block' in nodes
        assert 'EndBlock' in nodes

    def test_for_loop(self):
        nodes = _tokens_to_structural_nodes(
            tokenize("for (int i = 0; i < n; i++) { }"))
        assert 'ForLoop' in nodes
        assert 'Block' in nodes

    def test_while_loop(self):
        nodes = _tokens_to_structural_nodes(tokenize("while (cond) { }"))
        assert 'WhileLoop' in nodes

    def test_return_stmt(self):
        nodes = _tokens_to_structural_nodes(tokenize("return x;"))
        assert 'ReturnStmt' in nodes
        assert 'StmtEnd' in nodes

    def test_function_call(self):
        nodes = _tokens_to_structural_nodes(tokenize("foo(x);"))
        assert 'CallExpr' in nodes

    def test_assignment(self):
        nodes = _tokens_to_structural_nodes(tokenize("x = 5;"))
        assert 'Assignment' in nodes

    def test_binary_expr(self):
        nodes = _tokens_to_structural_nodes(tokenize("a + b;"))
        assert 'BinaryExpr' in nodes

    def test_var_decl(self):
        nodes = _tokens_to_structural_nodes(tokenize("int x = 5;"))
        assert 'VarDecl' in nodes

    def test_try_catch(self):
        nodes = _tokens_to_structural_nodes(
            tokenize("try { } catch { }"))
        assert 'TryBlock' in nodes
        assert 'CatchBlock' in nodes

    def test_switch_case(self):
        nodes = _tokens_to_structural_nodes(
            tokenize("switch (x) { case 1: break; }"))
        assert 'SwitchStmt' in nodes
        assert 'CaseClause' in nodes
        assert 'BreakStmt' in nodes

    def test_renamed_vars_produce_same_nodes(self):
        """Logic clones with renamed variables should produce
        identical structural node sequences."""
        code_a = """
        int f(int a, int b) {
            if (a > b) {
                return a;
            }
            return b;
        }
        """
        code_b = """
        int g(int x, int y) {
            if (x > y) {
                return x;
            }
            return y;
        }
        """
        nodes_a = _tokens_to_structural_nodes(tokenize(code_a))
        nodes_b = _tokens_to_structural_nodes(tokenize(code_b))
        assert nodes_a == nodes_b

    def test_empty_tokens(self):
        assert _tokens_to_structural_nodes([]) == []


class TestNgramJaccard:
    def test_identical_sequences(self):
        seq = ['IfStmt', 'Block', 'ReturnStmt', 'StmtEnd', 'EndBlock']
        assert _ngram_jaccard(seq, seq, n=3) == 100.0

    def test_completely_different(self):
        seq_a = ['IfStmt', 'Block', 'ReturnStmt']
        seq_b = ['ForLoop', 'WhileLoop', 'CallExpr']
        assert _ngram_jaccard(seq_a, seq_b, n=2) == 0.0

    def test_empty_both(self):
        assert _ngram_jaccard([], [], n=3) == 100.0

    def test_one_empty(self):
        assert _ngram_jaccard(['A', 'B', 'C'], [], n=2) == 0.0

    def test_partial_overlap(self):
        seq_a = ['A', 'B', 'C', 'D']
        seq_b = ['A', 'B', 'C', 'E']
        score = _ngram_jaccard(seq_a, seq_b, n=2)
        assert 0 < score < 100

    def test_unigrams(self):
        seq_a = ['A', 'B', 'C']
        seq_b = ['A', 'B', 'D']
        score = _ngram_jaccard(seq_a, seq_b, n=1)
        # A and B are shared, C and D are unique → 2/4 = 50%
        assert score == pytest.approx(50.0)


class TestAstSequenceScore:
    def test_identical_code(self):
        code = "int f(int x) { return x + 1; }"
        tokens = tokenize(code)
        score = _ast_sequence_score(tokens, tokens)
        assert score == 100.0

    def test_renamed_vars_high(self):
        code_a = """
        int findMax(int arr[], int n) {
            int maxVal = arr[0];
            for (int i = 1; i < n; i++) {
                if (arr[i] > maxVal) {
                    maxVal = arr[i];
                }
            }
            return maxVal;
        }
        """
        code_b = """
        int getLargest(int data[], int count) {
            int biggest = data[0];
            for (int j = 1; j < count; j++) {
                if (data[j] > biggest) {
                    biggest = data[j];
                }
            }
            return biggest;
        }
        """
        tokens_a = tokenize(code_a)
        tokens_b = tokenize(code_b)
        score = _ast_sequence_score(tokens_a, tokens_b)
        assert score > 80.0

    def test_empty_tokens(self):
        assert _ast_sequence_score([], []) == 0.0


# ═══════════════════════════════════════════════════════════════════════
# Public API — semantic_similarity() end-to-end
# ═══════════════════════════════════════════════════════════════════════

class TestSemanticSimilarity:
    """Tests for semantic_similarity()."""

    def test_empty_inputs(self):
        assert semantic_similarity([], []) == 0.0

    def test_identical_code(self):
        code = "int add(int a, int b) { return a + b; }"
        tokens = tokenize(code)
        score = semantic_similarity(tokens, tokens, "int", "int", 2, 2)
        assert score > 80.0

    def test_same_return_type_boost(self):
        code_a = "int f(int x) { return x + 1; }"
        code_b = "int g(int y) { return y + 2; }"
        tokens_a = tokenize(code_a)
        tokens_b = tokenize(code_b)
        score = semantic_similarity(tokens_a, tokens_b, "int", "int", 1, 1)
        assert score > 60.0

    def test_different_return_type(self):
        code_a = "int f(int x) { return x; }"
        code_b = "void g(int y) { cout << y; }"
        tokens_a = tokenize(code_a)
        tokens_b = tokenize(code_b)
        score_same = semantic_similarity(tokens_a, tokens_b, "int", "int", 1, 1)
        score_diff = semantic_similarity(tokens_a, tokens_b, "int", "void", 1, 1)
        # Same return type should score higher
        assert score_same >= score_diff

    def test_param_count_similarity(self):
        tokens = tokenize("int f(int a) { return a; }")
        score_same = semantic_similarity(tokens, tokens, "int", "int", 1, 1)
        score_diff = semantic_similarity(tokens, tokens, "int", "int", 1, 5)
        assert score_same >= score_diff

    def test_control_flow_match(self):
        code_a = """
        void f(int n) {
            for (int i = 0; i < n; i++) {
                if (i > 5) break;
            }
        }
        """
        code_b = """
        void g(int m) {
            for (int j = 0; j < m; j++) {
                if (j > 5) break;
            }
        }
        """
        tokens_a = tokenize(code_a)
        tokens_b = tokenize(code_b)
        score = semantic_similarity(tokens_a, tokens_b, "void", "void", 1, 1)
        assert score > 70.0

    def test_scores_bounded(self):
        """All scores should be between 0 and 100."""
        code = "int f(int x) { return x * 2; }"
        tokens = tokenize(code)
        score = semantic_similarity(tokens, tokens, "int", "int", 1, 1)
        assert 0 <= score <= 100
