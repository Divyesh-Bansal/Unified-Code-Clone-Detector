# Unified Code Clone Detection Tool

A tool that detects similar/duplicate functions in C++/Java/C# source code.

## Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. Clone or download the project

2. Navigate to the project directory:
```bash
cd my_tool
```

3. Create a virtual environment:
```bash
python -m venv venv
```

4. Activate the virtual environment:

   **On Windows:**
   ```bash
   venv\Scripts\activate
   ```

   **On macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

5. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Tool

### Basic Command

```bash
python -m my_tool <path> [--threshold <value>] [--output <file>] [--mode <mode>]
```

### Arguments

- **`<path>`** (required): Path to a source file or directory containing files to analyze
- **`--threshold`** or **`-t`** (optional): Minimum similarity percentage to report (default: 50, range: 0-100)
- **`--output`** or **`-o`** (optional): Output report file path (default: report.txt)
- **`--mode`** or **`-m`** (optional): Detection mode - `fxn` or `file` (default: fxn)

### Direct Command Examples

**Analyze a single file (function-level):**
```bash
python -m my_tool path/to/file.cpp
```


### PowerShell Scripts (Windows)

#### run.ps1
Runs the tool on a specified directory with formatted output and timing information.

**Usage:**
```powershell
.\run.ps1 -TargetFolder <path>
```
in run.ps1 is the ouptut final_result.txt , threshold is 50 and mode is file

**Example:**
```powershell
.\run.ps1 -TargetFolder test_input
.\run.ps1 -TargetFolder ./src
```

**What it does:**
- Takes a target folder path as input
- Runs the tool with `--threshold 50` and `--mode file` 
- Saves results to `final_result.txt`
- Displays formatted output with timing information

#### run_batches.ps1
Runs hardcoded batches from the SOCO dataset for batch testing.
**Usage:**
```powershell
.\run_batches.ps1
```
**Note:** No parameters required. The script:
- Processes 10 predefined batches from the `soco/` directory
- Creates test directories in `batch_tests/`
- Runs file-level comparison with `--threshold 50`
- Generates individual report files (`test1.txt`, `test2.txt`, etc.)
- Automatically copies relevant SOCO folders for each batch

### Output

Results are displayed in the console and saved to the specified output file (default: `report.txt`).


Running on first 81 files of SOCO Dataset:
Precision: 93.75% 
Recall: 78.95% 
F1-Score: 85.73%

| Predicted: CLONE (16)| Predicted: NOT CLONE (3224)                         |
----------------------|------------------------|-----------------------------|
Actual: CLONE (19)    |   True Positive (TP)   |    False Negative (FN)      |
                      |          15            |             4               |
----------------------|------------------------|-----------------------------|
Actual: NOT CLONE     |  False Positive (FP)   |    True Negative (TN)       |
(3221)                |           1            |           3220              |
----------------------|------------------------|-----------------------------|



On SOCO:
Precision: 72.63%
Recall: 71.13%
F1-Score: 71.87%

| Predicted: CLONE (95)  | Predicted: NOT CLONE (33,316)|
----------------------|------------------------|------------------------------|
Actual: CLONE (97)    |   True Positive (TP)   |    False Negative (FN)       |
                      |          69            |             28               |
----------------------|------------------------|------------------------------|
Actual: NOT CLONE     |  False Positive (FP)   |    True Negative (TN)        |
(33,314)              |          26            |           33,288             |
----------------------|------------------------|------------------------------|
