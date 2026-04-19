"""Tests for feature extractor module."""

from my_tool.tokenizer import tokenize
from my_tool.java_tokenizer import tokenize_java
from my_tool.cs_tokenizer import tokenize_cs
from my_tool.similarity.feature_extractor import (
    extract_features,
    NUM_FEATURES,
    F_INVOKED_METHOD_ON,
    UNIFIED_TYPE_ENCODING,
    TYPE_ENCODING,
)


class TestFeatureExtractor:
    """Tests for extract_features()."""

    def test_empty_input(self):
        assert extract_features([]) == []

    def test_simple_declaration(self):
        code = "int x = 5;"
        tokens = tokenize(code)
        features = extract_features(tokens)
        assert len(features) > 0
        # x should be found
        names = [f.name for f in features]
        assert 'x' in names

    def test_feature_vector_length(self):
        code = "int x = 5;"
        tokens = tokenize(code)
        features = extract_features(tokens)
        for f in features:
            assert len(f.features) == NUM_FEATURES

    def test_loop_variable(self):
        code = """
        void f() {
            int sum = 0;
            for (int i = 0; i < 10; i++) {
                sum += i;
            }
        }
        """
        tokens = tokenize(code)
        features = extract_features(tokens)
        names = {f.name: f for f in features}
        # 'i' should be detected in a loop
        if 'i' in names:
            feats = names['i'].features
            # Feature for first-level loop should be positive
            assert feats[22] > 0  # F_IN_FIRST_LEVEL_LOOP

    def test_multiple_variables(self):
        code = "int a = 1; float b = 2.0; char c = 'x';"
        tokens = tokenize(code)
        features = extract_features(tokens)
        names = [f.name for f in features]
        assert 'a' in names
        assert 'b' in names
        assert 'c' in names

    def test_if_statement_detection(self):
        code = """
        void f() {
            int x = 5;
            if (x > 3) {
                x = 10;
            }
        }
        """
        tokens = tokenize(code)
        features = extract_features(tokens)
        names = {f.name: f for f in features}
        if 'x' in names:
            feats = names['x'].features
            assert feats[4] > 0  # F_IN_IF_STATEMENT


class TestNewFeatures:
    """Tests for F_INVOKED_METHOD_ON (index 26) and UNIFIED_TYPE_ENCODING."""

    # ── NUM_FEATURES sanity check ──────────────────────────────────────

    def test_num_features_is_27(self):
        """Feature vector must be exactly 27 elements after the upgrade."""
        assert NUM_FEATURES == 27

    # ── F_INVOKED_METHOD_ON ────────────────────────────────────────────

    def test_invoked_method_on_cpp(self):
        """C++: obj.push_back(v) should set F_INVOKED_METHOD_ON on obj."""
        code = """
        void f() {
            vector<int> obj;
            int v = 5;
            obj.push_back(v);
        }
        """
        features = extract_features(tokenize(code))
        names = {f.name: f for f in features}
        assert 'obj' in names, "obj should be extracted as a variable"
        assert names['obj'].features[F_INVOKED_METHOD_ON] > 0

    def test_invoked_method_on_java(self):
        """Java: list.add(x) should set F_INVOKED_METHOD_ON on list."""
        code = """
        void f() {
            ArrayList list = new ArrayList();
            int x = 1;
            list.add(x);
        }
        """
        features = extract_features(tokenize_java(code))
        names = {f.name: f for f in features}
        assert 'list' in names, "list should be extracted as a variable"
        assert names['list'].features[F_INVOKED_METHOD_ON] > 0

    def test_invoked_method_on_cs(self):
        """C#: dict.Add(k, v) should set F_INVOKED_METHOD_ON on dict."""
        code = """
        void f() {
            Dictionary dict = new Dictionary();
            int k = 1;
            dict.Add(k, 2);
        }
        """
        features = extract_features(tokenize_cs(code))
        names = {f.name: f for f in features}
        assert 'dict' in names, "dict should be extracted as a variable"
        assert names['dict'].features[F_INVOKED_METHOD_ON] > 0

    def test_no_method_on_for_plain_call(self):
        """foo(x) must NOT set F_INVOKED_METHOD_ON on x."""
        code = """
        void f() {
            int x = 1;
            foo(x);
        }
        """
        features = extract_features(tokenize(code))
        names = {f.name: f for f in features}
        if 'x' in names:
            assert names['x'].features[F_INVOKED_METHOD_ON] == 0

    # ── UNIFIED_TYPE_ENCODING cross-language mappings ──────────────────

    def test_unified_boolean_types(self):
        """bool (C++/C#) and boolean (Java) must map to the same code."""
        assert UNIFIED_TYPE_ENCODING['bool'] == UNIFIED_TYPE_ENCODING['boolean']
        assert UNIFIED_TYPE_ENCODING['bool'] == UNIFIED_TYPE_ENCODING['Boolean']
        assert UNIFIED_TYPE_ENCODING['bool'] == 7

    def test_unified_string_types(self):
        """string (C++/C#) and String (Java) must map to the same code."""
        assert UNIFIED_TYPE_ENCODING['string'] == UNIFIED_TYPE_ENCODING['String']
        assert UNIFIED_TYPE_ENCODING['string'] == 4

    def test_unified_container_types(self):
        """vector (C++), List/ArrayList (Java), List (C#) share code 8."""
        code = UNIFIED_TYPE_ENCODING['vector']
        assert code == 8
        assert UNIFIED_TYPE_ENCODING['List']      == code
        assert UNIFIED_TYPE_ENCODING['ArrayList'] == code
        assert UNIFIED_TYPE_ENCODING['IList']     == code

    def test_unified_map_types(self):
        """map (C++), HashMap (Java), Dictionary (C#) share code 9."""
        code = UNIFIED_TYPE_ENCODING['map']
        assert code == 9
        assert UNIFIED_TYPE_ENCODING['HashMap']    == code
        assert UNIFIED_TYPE_ENCODING['Dictionary'] == code

    def test_unified_integer_types(self):
        """int, Long, uint, sbyte etc. all share code 1."""
        for t in ('int', 'long', 'short', 'unsigned', 'signed',
                  'byte', 'Integer', 'Long',
                  'uint', 'ulong', 'sbyte', 'nint'):
            assert UNIFIED_TYPE_ENCODING[t] == 1, f"{t!r} should resolve to 1"

    def test_type_encoding_alias(self):
        """TYPE_ENCODING must be the same object as UNIFIED_TYPE_ENCODING."""
        assert TYPE_ENCODING is UNIFIED_TYPE_ENCODING

    def test_feature_vector_length_after_upgrade(self):
        """Each extracted feature vector must have exactly NUM_FEATURES=27 entries."""
        code = "int x = 5;"
        for feat in extract_features(tokenize(code)):
            assert len(feat.features) == NUM_FEATURES
