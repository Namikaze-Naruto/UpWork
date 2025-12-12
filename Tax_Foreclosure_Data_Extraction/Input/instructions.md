# Instructions

## Prerequisites
- Python 3.8+
- Libraries: `pandas`, `pdfplumber`, `openpyxl`
    ```bash
    pip install pandas pdfplumber openpyxl
    ```

## Usage
1. Open the `Processing` folder.
2. Run `final_extractor.py`.
    ```bash
    python final_extractor.py
    ```
3. The script will read PDFs from the `Input` folder (you may need to adjust paths in the script if running from a different location, currently configured for a flat structure or relative paths). 
   *Note: The script expects input files to be available. If you moved them to `Input`, ensure the script points to `../Input/filename.pdf` or move the script to the root.*

## Output
- Output files will be generated in the current directory (or `Output` folder if script is modified).
- Formats:
    - `.xlsx`: Excel spreadsheet
    - `.txt`: Colon-separated text file
