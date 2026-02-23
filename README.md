# Hybrid C++ Code Clone Detection Tool

A Python-based tool that detects similar/duplicate functions in C++ source code using a **hybrid ensemble** of three complementary algorithms.

## Quick Start

```bash
# Create virtual environment and install dependencies
cd /home/pramod/cd/my_tool
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run on a directory of C++ files
python -m my_tool test_input/ --threshold 60

# Run on a single file
python -m my_tool path/to/file.cpp --threshold 50

# Custom output file
python -m my_tool test_input/ --threshold 60 --output results.txt
```

## Algorithms

The tool combines three similarity algorithms into a weighted ensemble:

| Algorithm | Weight | Description |
|---|---|---|
| **LexicalDetector** | 50% | Token-based: TF-IDF Cosine Similarity + LCS, weighted by method size ratio |
| **StructuralDetector** | 35% | Full pipeline: 26-feature variable profiles → Hungarian optimal variable mapping → Euclidean distance with that mapping |
| **SemanticDetector** | 15% | Structural: return types, parameter counts, control flow patterns, token distributions |

### Confidence Classification

| Score | Confidence |
|---|---|
| > 90% | VERY HIGH |
| > 75% | HIGH |
| > 60% | MEDIUM |
| ≤ 60% | LOW |

## Output

### Console
```
============================================================
  HYBRID CODE CLONE DETECTION RESULTS
============================================================
  Pair #1:
    file1.cpp: add (line 5)
    file2.cpp: addition (line 5)
    Lexical: 100.0%  |  Structural: 100.0%  |  Semantic: 100.0%
    ──> HYBRID SCORE: 100.00%  [VERY HIGH]
```

### report.txt
Automatically generated with:
- Timestamp and configuration
- All similar pairs with individual algorithm scores
- Hybrid score and confidence level
- Summary statistics and confidence distribution

## Supported Files

- `.cpp`, `.h`, `.hpp`, `.cc`, `.cxx`

## Project Structure

```
my_tool/
├── my_tool/
│   ├── main.py              # CLI entry point
│   ├── tokenizer.py          # C++ regex tokenizer
│   ├── normalizer.py         # Variable renaming (id0, id1...)
│   ├── method_extractor.py   # Function extraction via brace matching
│   ├── report.py             # Report generation
│   └── similarity/
│       ├── cosine.py         # TF-IDF Cosine Similarity
│       ├── lcs.py            # Longest Common Subsequence
│       ├── lexical.py        # LexicalDetector combined score
│       ├── feature_extractor.py  # 26-feature variable profiles
│       ├── euclidean.py      # Euclidean distance (StructuralDetector)
│       ├── hungarian.py      # Hungarian Algorithm (optimal variable mapping)
│       ├── semantic.py       # SemanticDetector
│       └── hybrid.py         # Weighted ensemble
├── tests/                    # 103 unit + integration tests
│   ├── sample_files/         # Test C++ files
│   └── test_*.py
└── test_input/               # Sample input directory
```

## Testing

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

## Error Handling

- Invalid file paths → clear error messages
- Non-C++ files → rejected with supported extensions listed
- Malformed C++ → gracefully skipped with warnings
- Empty files/directories → informative messages
- Threshold validation → must be 0-100


`my_tool = 50% LexicalDetector + 35% StructuralDetector + 15% SemanticDetector`

- **LexicalDetector** — token-based: TF-IDF Cosine + LCS × size ratio
- **StructuralDetector** — variable feature extraction → Hungarian optimal mapping → mapped Euclidean distance
- **SemanticDetector** — return type, parameter count, control flow, token distribution analysis
