"""
Report Generator Module

Generates report.txt output with detailed similarity analysis results,
including per-pair individual algorithm scores and summary statistics.
"""

import os
from datetime import datetime
from typing import List, NamedTuple

from my_tool.similarity.hybrid import SimilarityResult


class MethodPairResult(NamedTuple):
    """Result of comparing two methods."""
    file_a: str
    func_a: str
    line_a: int
    file_b: str
    func_b: str
    line_b: int
    result: SimilarityResult
    language: str = "C++"


def _rel(filepath: str, base: str) -> str:
    """Return filepath relative to base directory (or base file's directory)."""
    try:
        base_dir = base if os.path.isdir(base) else os.path.dirname(os.path.abspath(base))
        return os.path.relpath(filepath, base_dir)
    except ValueError:
        return filepath


def generate_report(results: List[MethodPairResult],
                    input_path: str,
                    threshold: float,
                    output_path: str = "report.txt",
                    total_files: int = 0,
                    total_functions: int = 0,
                    mode: str = 'fxn') -> str:
    """
    Generate a detailed report.txt file with similarity analysis results.

    Args:
        results: List of MethodPairResult for all similar pairs.
        input_path: The input path that was analyzed.
        threshold: The similarity threshold used.
        output_path: Path for the output report file.
        total_files: Total number of files analyzed.
        total_functions: Total number of functions analyzed.

    Returns:
        The full path to the generated report file.

    Raises:
        IOError: If the report file cannot be written.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 72 + "\n")
            f.write("     HYBRID CODE CLONE DETECTION TOOL - ANALYSIS REPORT\n")
            f.write("=" * 72 + "\n\n")

            f.write(f"  Timestamp     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"  Input Path    : {input_path}\n")
            f.write(f"  Detection Mode: {'File-Level' if mode == 'file' else 'Function-Level'}\n")
            f.write(f"  Threshold     : {threshold}%\n")
            f.write(f"  Total Files   : {total_files}\n")
            if mode != 'file':
                f.write(f"  Total Functions: {total_functions}\n")
            f.write(f"  Similar Pairs : {len(results)}\n")
            f.write("\n" + "-" * 72 + "\n")

            if not results:
                f.write("\n  No similar function pairs found above the threshold.\n")
                f.write("\n" + "=" * 72 + "\n")
                return os.path.abspath(output_path)

            if mode == 'file':
                f.write("\n  SIMILAR FILE PAIRS\n")
            else:
                f.write("\n  SIMILAR FUNCTION PAIRS\n")
            f.write("-" * 72 + "\n\n")

            for idx, pair in enumerate(results, 1):
                r = pair.result
                lang_tag = f"[{pair.language}]"

                f.write(f"  Pair #{idx}  {lang_tag}\n")
                f.write(f"  {'─' * 40}\n")
                f.write(f"    File A    : {_rel(pair.file_a, input_path)}\n")
                if mode != 'file':
                    f.write(f"    Function A: {pair.func_a} (line {pair.line_a})\n")
                f.write(f"    File B    : {_rel(pair.file_b, input_path)}\n")
                if mode != 'file':
                    f.write(f"    Function B: {pair.func_b} (line {pair.line_b})\n")
                f.write(f"\n")
                f.write(f"    Individual Algorithm Scores:\n")
                f.write(f"      ├── LexicalDetector   : {r.lexical_score:6.2f}%\n")
                f.write(f"      ├── StructuralDetector: {r.structural_score:6.2f}%\n")
                f.write(f"      └── SemanticDetector  : {r.semantic_score:6.2f}%\n")
                f.write(f"\n")
                f.write(f"    ╔══════════════════════════════════════════════╗\n")
                f.write(f"    ║  HYBRID SCORE: {r.hybrid_score:6.2f}%  ║\n")
                f.write(f"    ╚══════════════════════════════════════════════╝\n")
                f.write(f"\n")

            # Summary
            f.write("-" * 72 + "\n")
            f.write("  SUMMARY\n")
            f.write("-" * 72 + "\n\n")

            # Confidence distribution
            very_high = sum(1 for p in results if p.result.confidence == "VERY HIGH")
            high = sum(1 for p in results if p.result.confidence == "HIGH")
            medium = sum(1 for p in results if p.result.confidence == "MEDIUM")
            low = sum(1 for p in results if p.result.confidence == "LOW")

            f.write(f"  Confidence Distribution:\n")
            f.write(f"    VERY HIGH (>90%): {very_high} pairs\n")
            f.write(f"    HIGH      (>75%): {high} pairs\n")
            f.write(f"    MEDIUM    (>60%): {medium} pairs\n")
            f.write(f"    LOW       (≤60%): {low} pairs\n")
            f.write(f"\n")

            # Language distribution
            lang_counts = {}
            for p in results:
                lang_counts[p.language] = lang_counts.get(p.language, 0) + 1
            if len(lang_counts) > 1:
                f.write(f"  Language Distribution:\n")
                for lang, count in sorted(lang_counts.items()):
                    f.write(f"    {lang:10s}: {count} pairs\n")
                f.write(f"\n")

            if results:
                scores = [p.result.hybrid_score for p in results]
                f.write(f"  Score Statistics:\n")
                f.write(f"    Highest : {max(scores):.2f}%\n")
                f.write(f"    Lowest  : {min(scores):.2f}%\n")
                f.write(f"    Average : {sum(scores) / len(scores):.2f}%\n")

            f.write(f"\n" + "=" * 72 + "\n")
            f.write(f"  End of Report\n")
            f.write(f"=" * 72 + "\n")

    except IOError as e:
        raise IOError(f"Failed to write report to {output_path}: {e}")

    return os.path.abspath(output_path)


def format_console_output(results: List[MethodPairResult],
                          input_path: str,
                          threshold: float,
                          total_files: int = 0,
                          total_functions: int = 0,
                          mode: str = 'fxn') -> str:
    """
    Format results for console output.

    Args:
        results: List of MethodPairResult.
        input_path: Input path analyzed.
        threshold: Similarity threshold used.
        total_files: Total files analyzed.
        total_functions: Total functions analyzed.

    Returns:
        Formatted string for console display.
    """
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("  HYBRID CODE CLONE DETECTION RESULTS")
    lines.append("=" * 60)
    lines.append(f"  Input: {input_path}")
    lines.append(f"  Mode: {'File-Level' if mode == 'file' else 'Function-Level'}")
    lines.append(f"  Threshold: {threshold}%")
    if mode == 'file':
        lines.append(f"  Files: {total_files}  |  Similar Pairs: {len(results)}")
    else:
        lines.append(f"  Files: {total_files}  |  Functions: {total_functions}  "
                     f"|  Similar Pairs: {len(results)}")
    lines.append("-" * 60)

    if not results:
        lines.append("")
        if mode == 'file':
            lines.append("  No similar file pairs found.")
        else:
            lines.append("  No similar function pairs found.")
        lines.append("=" * 60)
        return "\n".join(lines)

    for idx, pair in enumerate(results, 1):
        r = pair.result
        lang_tag = f"[{pair.language}]"
        lines.append("")
        lines.append(f"  Pair #{idx}:  {lang_tag}")
        if mode == 'file':
            lines.append(f"    {_rel(pair.file_a, input_path)}")
            lines.append(f"    {_rel(pair.file_b, input_path)}")
        else:
            lines.append(f"    {_rel(pair.file_a, input_path)}: {pair.func_a} (line {pair.line_a})")
            lines.append(f"    {_rel(pair.file_b, input_path)}: {pair.func_b} (line {pair.line_b})")
        lines.append(f"    Lexical: {r.lexical_score:.1f}%  |  Structural: {r.structural_score:.1f}%  |  Semantic: {r.semantic_score:.1f}%")
        lines.append(f"    ──> HYBRID SCORE: {r.hybrid_score:.2f}%  [{r.confidence}]")

    lines.append("")
    lines.append("-" * 60)
    lines.append(f"  Total similar pairs found: {len(results)}")
    lines.append("=" * 60)
    lines.append("")

    return "\n".join(lines)
