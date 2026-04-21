"""
Hybrid Code Clone Detection Tool - Main Entry Point

Usage:
    python -m my_tool <path> [--threshold 60] [--output report.txt] [--mode fxn|file]

Where:
    <path>      Path to a .cpp/.h/.java file or directory containing source files
    --threshold Minimum similarity percentage to report (default: 60)
    --output    Path for the output report file (default: report.txt)
    --mode      Detection mode: 'fxn' (per-function) or 'file' (per-file)
"""

import argparse
import os
import sys
from typing import Dict, List, Tuple

from my_tool.tokenizer import tokenize_file, Token
from my_tool.method_extractor import extract_methods, MethodInfo
from my_tool.java_tokenizer import tokenize_java_file
from my_tool.java_method_extractor import extract_java_methods
from my_tool.cs_tokenizer import tokenize_cs_file
from my_tool.cs_method_extractor import extract_cs_methods
from my_tool.normalizer import normalize
from my_tool.similarity.hybrid import compute_hybrid_similarity
from my_tool.similarity.feature_extractor import extract_features
from my_tool.file_compare import compute_file_similarity
from my_tool.report import (
    MethodPairResult,
    generate_report,
    format_console_output,
)


# Supported file extensions grouped by language
CPP_EXTENSIONS = {'.cpp', '.h', '.hpp', '.cc', '.cxx'}
JAVA_EXTENSIONS = {'.java'}
CS_EXTENSIONS = {'.cs'}
ALL_EXTENSIONS = CPP_EXTENSIONS | JAVA_EXTENSIONS | CS_EXTENSIONS


def find_source_files(path: str) -> List[str]:
    """
    Find all supported source files (C++ and Java) in a path.

    Args:
        path: File or directory path.

    Returns:
        List of absolute file paths.

    Raises:
        FileNotFoundError: If path doesn't exist.
        ValueError: If path is a file but not a supported source file.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")

    if os.path.isfile(path):
        ext = os.path.splitext(path)[1].lower()
        if ext not in ALL_EXTENSIONS:
            raise ValueError(
                f"File '{path}' is not a supported source file. "
                f"Supported extensions: {', '.join(sorted(ALL_EXTENSIONS))}"
            )
        return [os.path.abspath(path)]

    # Directory: recursively find source files
    files = []
    for root, _, filenames in os.walk(path):
        for filename in sorted(filenames):
            ext = os.path.splitext(filename)[1].lower()
            if ext in ALL_EXTENSIONS:
                files.append(os.path.abspath(os.path.join(root, filename)))

    if not files:
        print(f"Warning: No supported source files found in '{path}'",
              file=sys.stderr)

    return files


# Keep the old name as an alias for backward compatibility with tests
find_cpp_files = find_source_files


def group_files_by_language(files: List[str]) -> Dict[str, List[str]]:
    """
    Group files by language based on extension.

    Args:
        files: List of file paths.

    Returns:
        Dict with keys 'cpp', 'java', and 'cs', each mapping to a list of paths.
    """
    groups: Dict[str, List[str]] = {'cpp': [], 'java': [], 'cs': []}
    for filepath in files:
        ext = os.path.splitext(filepath)[1].lower()
        if ext in CPP_EXTENSIONS:
            groups['cpp'].append(filepath)
        elif ext in JAVA_EXTENSIONS:
            groups['java'].append(filepath)
        elif ext in CS_EXTENSIONS:
            groups['cs'].append(filepath)
    return groups


def extract_all_methods(files: List[str]) -> List[Tuple[str, MethodInfo]]:
    """
    Extract methods from all C++ files.

    Args:
        files: List of C++ file paths.

    Returns:
        List of (filepath, MethodInfo) tuples.
    """
    all_methods = []
    errors = []

    for filepath in files:
        try:
            tokens = tokenize_file(filepath)
            methods = extract_methods(tokens)
            for method in methods:
                all_methods.append((filepath, method))
        except (FileNotFoundError, IOError) as e:
            errors.append(f"  Warning: Skipping {filepath}: {e}")
        except Exception as e:
            errors.append(f"  Warning: Error processing {filepath}: {e}")

    if errors:
        for err in errors:
            print(err, file=sys.stderr)

    return all_methods


def extract_all_methods_java(files: List[str]) -> List[Tuple[str, MethodInfo]]:
    """
    Extract methods from all Java files.

    Args:
        files: List of Java file paths.

    Returns:
        List of (filepath, MethodInfo) tuples.
    """
    all_methods = []
    errors = []

    for filepath in files:
        try:
            tokens = tokenize_java_file(filepath)
            methods = extract_java_methods(tokens)
            for method in methods:
                all_methods.append((filepath, method))
        except (FileNotFoundError, IOError) as e:
            errors.append(f"  Warning: Skipping {filepath}: {e}")
        except Exception as e:
            errors.append(f"  Warning: Error processing {filepath}: {e}")

    if errors:
        for err in errors:
            print(err, file=sys.stderr)

    return all_methods


def extract_all_methods_cs(files: List[str]) -> List[Tuple[str, MethodInfo]]:
    """
    Extract methods from all C# files.

    Args:
        files: List of C# file paths.

    Returns:
        List of (filepath, MethodInfo) tuples.
    """
    all_methods = []
    errors = []

    for filepath in files:
        try:
            tokens = tokenize_cs_file(filepath)
            methods = extract_cs_methods(tokens)
            for method in methods:
                all_methods.append((filepath, method))
        except (FileNotFoundError, IOError) as e:
            errors.append(f"  Warning: Skipping {filepath}: {e}")
        except Exception as e:
            errors.append(f"  Warning: Error processing {filepath}: {e}")

    if errors:
        for err in errors:
            print(err, file=sys.stderr)

    return all_methods


def compare_all_methods(all_methods: List[Tuple[str, MethodInfo]],
                        threshold: float,
                        language: str = "C++") -> List[MethodPairResult]:
    """
    Compare all method pairs and find similar ones above threshold.

    Args:
        all_methods: List of (filepath, MethodInfo) tuples.
        threshold: Minimum similarity percentage.
        language: Language label for the results.

    Returns:
        List of MethodPairResult for pairs above threshold.
    """
    results = []
    n = len(all_methods)

    # Pre-compute normalized tokens once per method — O(n) — so the pair
    # loop doesn't call normalize() O(n²) times (each method appears in
    # n-1 pairs, so without caching it would be called n*(n-1) times).
    norm_cache: List[List[Token]] = [
        normalize(m.tokens)[0] for _, m in all_methods
    ]

    for i in range(n):
        for j in range(i + 1, n):
            file_a, method_a = all_methods[i]
            file_b, method_b = all_methods[j]

            # Skip very small methods (less than 6 tokens = trivial)
            if len(method_a.tokens) < 6 or len(method_b.tokens) < 6:
                continue

            try:
                result = compute_hybrid_similarity(
                    method_a.tokens, method_b.tokens,
                    method_a.return_type, method_b.return_type,
                    method_a.param_count, method_b.param_count,
                    norm_a=norm_cache[i],
                    norm_b=norm_cache[j],
                )

                if result.hybrid_score >= threshold:
                    results.append(MethodPairResult(
                        file_a=file_a,
                        func_a=method_a.name,
                        line_a=method_a.start_line,
                        file_b=file_b,
                        func_b=method_b.name,
                        line_b=method_b.start_line,
                        result=result,
                        language=language
                    ))
            except Exception as e:
                print(f"  Warning: Error comparing {method_a.name} vs "
                      f"{method_b.name}: {e}", file=sys.stderr)

    # Sort by hybrid score descending
    results.sort(key=lambda r: r.result.hybrid_score, reverse=True)
    return results


def _tokenize_file_for_language(filepath: str, language: str) -> List[Token]:
    """Tokenize a source file using the appropriate language tokenizer."""
    if language == 'java':
        return tokenize_java_file(filepath)
    elif language == 'cs':
        return tokenize_cs_file(filepath)
    else:
        return tokenize_file(filepath)


def _extract_methods_for_language(tokens: List[Token], language: str) -> List[MethodInfo]:
    """Extract methods using the appropriate language extractor."""
    if language == 'java':
        return extract_java_methods(tokens)
    elif language == 'cs':
        return extract_cs_methods(tokens)
    else:
        return extract_methods(tokens)


def _lang_label(language: str) -> str:
    """Map internal language key to display label."""
    return {'cpp': 'C++', 'java': 'Java', 'cs': 'C#'}.get(language, language)


def compare_file_pairs(files: List[str], threshold: float,
                       language: str = 'cpp') -> List[MethodPairResult]:
    """
    Compare all file pairs within a language group using file-level detection.

    Args:
        files:     List of file paths in the same language group.
        threshold: Minimum similarity percentage to report.
        language:  Internal language key ('cpp', 'java', 'cs').

    Returns:
        List of MethodPairResult for pairs above threshold.
    """
    results: List[MethodPairResult] = []
    n = len(files)
    label = _lang_label(language)

    # Pre-tokenize and extract methods for every file once
    file_tokens: List[List[Token]] = []
    file_methods: List[List[MethodInfo]] = []
    file_norms: List[List[Token]] = []
    file_features: List[list] = []
    valid: List[bool] = []

    for filepath in files:
        try:
            tokens = _tokenize_file_for_language(filepath, language)
            methods = _extract_methods_for_language(tokens, language)
            norm_tokens, _ = normalize(tokens)
            features = [extract_features(m.tokens) for m in methods]
            file_tokens.append(tokens)
            file_methods.append(methods)
            file_norms.append(norm_tokens)
            file_features.append(features)
            valid.append(True)
        except Exception as e:
            print(f"  Warning: Skipping {filepath}: {e}", file=sys.stderr)
            file_tokens.append([])
            file_methods.append([])
            file_norms.append([])
            file_features.append([])
            valid.append(False)

    for i in range(n):
        if not valid[i]:
            continue
        for j in range(i + 1, n):
            if not valid[j]:
                continue

            try:
                result = compute_file_similarity(
                    file_tokens[i], file_tokens[j],
                    file_methods[i], file_methods[j],
                    norm_a=file_norms[i],
                    norm_b=file_norms[j],
                    features_a=file_features[i],
                    features_b=file_features[j],
                )

                if result.hybrid_score >= threshold:
                    results.append(MethodPairResult(
                        file_a=files[i],
                        func_a="<file>",
                        line_a=0,
                        file_b=files[j],
                        func_b="<file>",
                        line_b=0,
                        result=result,
                        language=label,
                    ))
            except Exception as e:
                print(f"  Warning: Error comparing "
                      f"{os.path.basename(files[i])} vs "
                      f"{os.path.basename(files[j])}: {e}",
                      file=sys.stderr)

    results.sort(key=lambda r: r.result.hybrid_score, reverse=True)
    return results


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog='my_tool',
        description='Hybrid Code Clone Detection Tool - '
                    'Detects similar/duplicate functions in C++, Java, and C# '
                    'source files using an ensemble of LexicalDetector, '
                    'StructuralDetector, and SemanticDetector algorithms.',
        epilog='Example: python -m my_tool ./src --threshold 50'
    )

    parser.add_argument(
        'path',
        help='Path to a C++/Java/C# file or directory containing source files'
    )
    parser.add_argument(
        '--threshold', '-t',
        type=float,
        default=50.0,
        help='Minimum similarity percentage to report (default: 60)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='report.txt',
        help='Output report file path (default: report.txt)'
    )
    parser.add_argument(
        '--mode', '-m',
        choices=['fxn', 'file'],
        default='fxn',
        help="Detection mode: 'fxn' (per-function, default) or 'file' (per-file)"
    )

    args = parser.parse_args()

    # Validate threshold
    if not 0 <= args.threshold <= 100:
        print("Error: Threshold must be between 0 and 100.", file=sys.stderr)
        sys.exit(1)

    # Find source files
    try:
        files = find_source_files(args.path)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not files:
        print("No supported source files found to analyze.", file=sys.stderr)
        sys.exit(1)

    # Group files by language
    groups = group_files_by_language(files)
    cpp_files = groups['cpp']
    java_files = groups['java']
    cs_files = groups['cs']

    print(f"\nAnalyzing {len(files)} source file(s) "
          f"({len(cpp_files)} C++, {len(java_files)} Java, {len(cs_files)} C#)...")

    mode = args.mode

    if mode == 'file':
        # ── File-level detection ──────────────────────────────────
        print(f"Mode: file-level comparison")

        all_results: List[MethodPairResult] = []

        for lang_key, lang_files in [('cpp', cpp_files),
                                      ('java', java_files),
                                      ('cs', cs_files)]:
            if len(lang_files) < 2:
                continue
            pairs_count = len(lang_files) * (len(lang_files) - 1) // 2
            print(f"Comparing {pairs_count} {_lang_label(lang_key)} file pair(s)...")
            lang_results = compare_file_pairs(
                lang_files, args.threshold, language=lang_key,
            )
            all_results.extend(lang_results)

        if not all_results:
            print("No similar file pairs found above the threshold.")

        all_results.sort(key=lambda r: r.result.hybrid_score, reverse=True)

        # Console output
        console_output = format_console_output(
            all_results, args.path, args.threshold,
            total_files=len(files),
            total_functions=0,
            mode='file',
        )
        print(console_output)

        # Generate report file
        try:
            report_path = generate_report(
                all_results, args.path, args.threshold,
                output_path=args.output,
                total_files=len(files),
                total_functions=0,
                mode='file',
            )
            print(f"Report saved to: {report_path}")
        except IOError as e:
            print(f"Error writing report: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        # ── Function-level detection (existing pipeline) ──────────
        # Extract methods per language group
        all_methods_cpp = extract_all_methods(cpp_files) if cpp_files else []
        all_methods_java = extract_all_methods_java(java_files) if java_files else []
        all_methods_cs = extract_all_methods_cs(cs_files) if cs_files else []

        total_functions = len(all_methods_cpp) + len(all_methods_java) + len(all_methods_cs)

        if total_functions == 0:
            print("No functions found in the provided files.")
            sys.exit(0)

        if total_functions < 2 and len(all_methods_cpp) < 2 and len(all_methods_java) < 2 and len(all_methods_cs) < 2:
            print("Need at least two functions in the same language to compare.")
            sys.exit(0)

        print(f"Found {total_functions} function(s) "
              f"({len(all_methods_cpp)} C++, {len(all_methods_java)} Java, {len(all_methods_cs)} C#).")

        # Compare within each language group independently
        all_results: List[MethodPairResult] = []

        if len(all_methods_cpp) >= 2:
            cpp_pairs = len(all_methods_cpp) * (len(all_methods_cpp) - 1) // 2
            print(f"Comparing {cpp_pairs} C++ pair(s)...")
            cpp_results = compare_all_methods(
                all_methods_cpp, args.threshold, language="C++")
            all_results.extend(cpp_results)

        if len(all_methods_java) >= 2:
            java_pairs = len(all_methods_java) * (len(all_methods_java) - 1) // 2
            print(f"Comparing {java_pairs} Java pair(s)...")
            java_results = compare_all_methods(
                all_methods_java, args.threshold, language="Java")
            all_results.extend(java_results)

        if len(all_methods_cs) >= 2:
            cs_pairs = len(all_methods_cs) * (len(all_methods_cs) - 1) // 2
            print(f"Comparing {cs_pairs} C# pair(s)...")
            cs_results = compare_all_methods(
                all_methods_cs, args.threshold, language="C#")
            all_results.extend(cs_results)

        # Sort merged results by hybrid score descending
        all_results.sort(key=lambda r: r.result.hybrid_score, reverse=True)

        # Console output
        console_output = format_console_output(
            all_results, args.path, args.threshold,
            total_files=len(files),
            total_functions=total_functions
        )
        print(console_output)

        # Generate report file
        try:
            report_path = generate_report(
                all_results, args.path, args.threshold,
                output_path=args.output,
                total_files=len(files),
                total_functions=total_functions
            )
            print(f"Report saved to: {report_path}")
        except IOError as e:
            print(f"Error writing report: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
