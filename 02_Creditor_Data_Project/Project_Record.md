# Project Record: Creditor Data Extraction

**Date**: 2025-12-14
**Objective**: Transform vertical creditor address data from `data.txt` into a flattened CSV format.

## Directory Structure
- `Input/`: Contains raw source data (`data.txt`).
- `Processing/`: Contains the Python extraction script (`extract_data.py`).
- `Output/`: Contains the final CSV file (`extracted_data.csv`).

## Process
1.  **Analysis**: identified creditor data blocks labeled "Priority" and "Nonpriority" starting around row 491.
2.  **Logic**: Developed a Python script to:
    -   Parse multi-line address blocks.
    -   Apply heuristics to separate Name from Address 1 when combined.
    -   Skip unrelated quoted blocks (e.g. Record IDs `3.104` or Checkbox labels `□`).
    -   Extract Amount.
3.  **Scope**: Initially targeted rows 491-3591, then expanded to the entire file per user request.

## Outcome
-   **Input Data**: ~12,700 lines.
-   **Extracted Records**: 924.
-   **Columns**: Name, Address 1, Address 2, City, State, Zip, Amount.
