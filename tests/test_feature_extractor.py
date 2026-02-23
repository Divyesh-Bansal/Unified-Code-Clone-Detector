"""Tests for feature extractor module."""

from my_tool.tokenizer import tokenize
from my_tool.similarity.feature_extractor import extract_features, NUM_FEATURES


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
