"""
Hybrid Code Clone Detection Tool - Main Entry Point

Usage:
    python -m my_tool <path> [--threshold 60] [--output report.txt]

Where:
    <path>      Path to a .cpp/.h file or directory containing C++ files
    --threshold Minimum similarity percentage to report (default: 60)
    --output    Path for the output report file (default: report.txt)
"""

import argparse
import os
import sys
from typing import List, Tuple

from my_tool.tokenizer import tokenize_file, Token
from my_tool.method_extractor import extract_methods, MethodInfo
from my_tool.similarity.hybrid import compute_hybrid_similarity
from my_tool.report import (
    MethodPairResult,
    generate_report,
    format_console_output,
)


def find_cpp_files(path: str) -> List[str]:
    """
    Find all C++ source files (.cpp, .h, .hpp, .cc, .cxx) in a path.

    Args:
        path: File or directory path.

    Returns:
        List of absolute file paths.

    Raises:
        FileNotFoundError: If path doesn't exist.
        ValueError: If path is a file but not a C++ file.
    """
    cpp_extensions = {'.cpp', '.h', '.hpp', '.cc', '.cxx'}

    if not os.path.exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")

    if os.path.isfile(path):
        ext = os.path.splitext(path)[1].lower()
        if ext not in cpp_extensions:
            raise ValueError(
                f"File '{path}' is not a C++ file. "
                f"Supported extensions: {', '.join(sorted(cpp_extensions))}"
            )
        return [os.path.abspath(path)]

    # Directory: recursively find C++ files
    files = []
    for root, _, filenames in os.walk(path):
        for filename in sorted(filenames):
            ext = os.path.splitext(filename)[1].lower()
            if ext in cpp_extensions:
                files.append(os.path.abspath(os.path.join(root, filename)))

    if not files:
        print(f"Warning: No C++ files found in '{path}'", file=sys.stderr)

    return files


def extract_all_methods(files: List[str]) -> List[Tuple[str, MethodInfo]]:
    """
    Extract methods from all files.

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


def compare_all_methods(all_methods: List[Tuple[str, MethodInfo]],
                        threshold: float) -> List[MethodPairResult]:
    """
    Compare all method pairs and find similar ones above threshold.

    Args:
        all_methods: List of (filepath, MethodInfo) tuples.
        threshold: Minimum similarity percentage.

    Returns:
        List of MethodPairResult for pairs above threshold.
    """
    results = []
    n = len(all_methods)

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
                    method_a.param_count, method_b.param_count
                )

                if result.hybrid_score >= threshold:
                    results.append(MethodPairResult(
                        file_a=file_a,
                        func_a=method_a.name,
                        line_a=method_a.start_line,
                        file_b=file_b,
                        func_b=method_b.name,
                        line_b=method_b.start_line,
                        result=result
                    ))
            except Exception as e:
                print(f"  Warning: Error comparing {method_a.name} vs "
                      f"{method_b.name}: {e}", file=sys.stderr)

    # Sort by hybrid score descending
    results.sort(key=lambda r: r.result.hybrid_score, reverse=True)
    return results


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog='my_tool',
        description='Hybrid C++ Code Clone Detection Tool - '
                    'Detects similar/duplicate functions in C++ source files '
                    'using an ensemble of LexicalDetector, StructuralDetector, '
                    'and SemanticDetector algorithms.',
        epilog='Example: python -m my_tool ./src --threshold 50'
    )

    parser.add_argument(
        'path',
        help='Path to a C++ file or directory containing C++ files'
    )
    parser.add_argument(
        '--threshold', '-t',
        type=float,
        default=60.0,
        help='Minimum similarity percentage to report (default: 60)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='report.txt',
        help='Output report file path (default: report.txt)'
    )

    args = parser.parse_args()

    # Validate threshold
    if not 0 <= args.threshold <= 100:
        print("Error: Threshold must be between 0 and 100.", file=sys.stderr)
        sys.exit(1)

    # Find C++ files
    try:
        files = find_cpp_files(args.path)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not files:
        print("No C++ files found to analyze.", file=sys.stderr)
        sys.exit(1)

    print(f"\nAnalyzing {len(files)} C++ file(s)...")

    # Extract methods
    all_methods = extract_all_methods(files)
    total_functions = len(all_methods)

    if total_functions == 0:
        print("No functions found in the provided files.")
        sys.exit(0)

    if total_functions < 2:
        print("Only one function found — need at least two to compare.")
        sys.exit(0)

    print(f"Found {total_functions} function(s). "
          f"Comparing {total_functions * (total_functions - 1) // 2} pairs...")

    # Compare all method pairs
    results = compare_all_methods(all_methods, args.threshold)

    # Console output
    console_output = format_console_output(
        results, args.path, args.threshold,
        total_files=len(files),
        total_functions=total_functions
    )
    print(console_output)

    # Generate report file
    try:
        report_path = generate_report(
            results, args.path, args.threshold,
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
