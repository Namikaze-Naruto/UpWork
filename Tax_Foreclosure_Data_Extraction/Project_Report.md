# Tax Foreclosure Data Extraction Project Report

## Project Overview
This project processes tax foreclosure data provided in text format for Wayne and Macomb counties. A Jupyter Notebook was developed to parse these text files, extract relevant fields (Tax ID, Address, Interested Parties, Amount), and export the data into structured formats.

## Folder Structure

### 1. `Input/`
Contains the raw data and instructions.
- **`processed/`**: Subfolder containing the text input files:
    - `wayne.txt`: Raw text data for Wayne County.
    - `macomb_tax`: Raw text data for Macomb County.
- **`2026_Wayne_County_Delinquent_Tax_Liens.pdf`**: Original PDF source (reference).
- **`2026 Macomb Tax foreclosure.pdf`**: Original PDF source (reference).
- **`sample 2026 Tax Foreclosure spreadsheet.xlsx`**: Target format reference.
- **`instructions.md`**: Basic usage instructions.

### 2. `Processing/`
Contains the code used to transform the data.
- **`Data_Extraction.ipynb`**: The Jupyter Notebook containing the parsing logic.
- **`Data_Extraction.py`**: Python script version of the notebook for automation.

### 3. `Output/`
Contains the final deliverables.
- **Wayne County**:
    - `Wayne_County_Final.xlsx`: Excel spreadsheet with expanded "Interested Parties" columns.
    - `Wayne_County_Final.txt`: Text file with Colon (`:`) separated values.
- **Macomb County**:
    - `Macomb_County_Final.xlsx`: Excel spreadsheet with expanded "Interested Parties" columns.
    - `Macomb_County_Final.txt`: Text file with Colon (`:`) separated values.

## Methodology

### Workflow
1.  **Input Analysis**: The text files (`wayne.txt` and `macomb_tax`) were analyzed to identify patterns.
    -   *Wayne*: Records separated by numeric Tax IDs, with subsequent lines representing Address and Parties.
    -   *Macomb*: Records separated by `Parcel ID#:`, with specific fields (`Amount`, `Address`, `Parties`) extracted via Regular Expressions.
2.  **Extraction Logic**:
    -   Implemented in `Data_Extraction.ipynb`.
    -   **Wayne Logic**: Iterates line-by-line, detecting "City of" headers and Tax ID patterns to group data.
    -   **Macomb Logic**: Splits text by Parcel ID and uses Regex to capture structured fields from unstructured blocks.
3.  **Data Transformation**:
    -   "Interested Parties" lists were expanded into separate columns (e.g., `Interested Party 1`, `Interested Party 2`).
    -   Data was cleaned (whitespace removal, noise filtering).
4.  **Export**:
    -   DataFrames saved to `.xlsx` for human readability.
    -   DataFrames saved to `.txt` using `:` delimiter for system compatibility.

## Execution
To run the extraction:
1.  Navigate to `Tax_Foreclosure_Data_Extraction/Processing/`.
2.  Open `Data_Extraction.ipynb` in Jupyter Notebook/Lab OR run `python Data_Extraction.py`.
3.  Outputs are generated in `Tax_Foreclosure_Data_Extraction/Output/`.

## Results
- **Wayne County**: Successfully parsed records from `wayne.txt`.
- **Macomb County**: Successfully parsed records from `macomb_tax`, including amounts and complex address blocks.
- **Zero Error Goal**: The logic targets high precision by using specific compiled Regex patterns for IDs and delimiters.
