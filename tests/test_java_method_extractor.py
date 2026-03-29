"""Tests for the Java method extractor module."""

import pytest
from my_tool.java_tokenizer import tokenize_java
from my_tool.java_method_extractor import extract_java_methods


class TestExtractJavaMethods:
    """Tests for the extract_java_methods() function."""

    def test_invalid_input(self):
        with pytest.raises(TypeError):
            extract_java_methods("not a list")

    def test_empty_list(self):
        assert extract_java_methods([]) == []

    def test_single_public_method(self):
        code = "public class Foo { public int add(int a, int b) { return a + b; } }"
        tokens = tokenize_java(code)
        methods = extract_java_methods(tokens)
        assert len(methods) == 1
        assert methods[0].name == 'add'
        assert methods[0].return_type == 'int'
        assert methods[0].param_count == 2

    def test_private_method(self):
        code = "class Foo { private void doWork() { System.out.println(1); } }"
        tokens = tokenize_java(code)
        methods = extract_java_methods(tokens)
        assert len(methods) == 1
        assert methods[0].name == 'doWork'
        assert methods[0].return_type == 'void'
        assert methods[0].param_count == 0

    def test_static_method(self):
        code = "class Foo { public static int compute(int x) { return x * 2; } }"
        tokens = tokenize_java(code)
        methods = extract_java_methods(tokens)
        assert len(methods) == 1
        assert methods[0].name == 'compute'
        assert methods[0].param_count == 1

    def test_multiple_methods(self):
        code = """
        public class Math {
            public int add(int a, int b) { return a + b; }
            public int sub(int a, int b) { return a - b; }
            private void print(int x) { System.out.println(x); }
        }
        """
        tokens = tokenize_java(code)
        methods = extract_java_methods(tokens)
        assert len(methods) == 3
        names = [m.name for m in methods]
        assert 'add' in names
        assert 'sub' in names
        assert 'print' in names

    def test_nested_braces(self):
        code = """
        class Foo {
            public int func(int n) {
                if (n > 0) {
                    for (int i = 0; i < n; i++) {
                        System.out.println(i);
                    }
                }
                return n;
            }
        }
        """
        tokens = tokenize_java(code)
        methods = extract_java_methods(tokens)
        assert len(methods) == 1
        assert methods[0].name == 'func'

    def test_constructor_skipped(self):
        code = """
        public class MyClass {
            public MyClass(int x) { this.x = x; }
            public int getX() { return x; }
        }
        """
        tokens = tokenize_java(code)
        methods = extract_java_methods(tokens)
        # Constructor should be skipped, only getX extracted
        names = [m.name for m in methods]
        assert 'MyClass' not in names
        assert 'getX' in names

    def test_method_with_throws(self):
        code = """
        class Foo {
            public void risky(int x) throws Exception {
                if (x < 0) throw new Exception();
            }
        }
        """
        tokens = tokenize_java(code)
        methods = extract_java_methods(tokens)
        assert len(methods) == 1
        assert methods[0].name == 'risky'

    def test_no_methods(self):
        code = "public class Empty { int x = 5; }"
        tokens = tokenize_java(code)
        methods = extract_java_methods(tokens)
        assert len(methods) == 0

    def test_protected_method(self):
        code = """
        class Foo {
            protected double calc(int a, int b, int c) {
                return (a + b) * c;
            }
        }
        """
        tokens = tokenize_java(code)
        methods = extract_java_methods(tokens)
        assert len(methods) == 1
        assert methods[0].name == 'calc'
        assert methods[0].param_count == 3

    def test_final_method(self):
        code = """
        class Foo {
            public final int getValue() { return 42; }
        }
        """
        tokens = tokenize_java(code)
        methods = extract_java_methods(tokens)
        assert len(methods) == 1
        assert methods[0].name == 'getValue'
