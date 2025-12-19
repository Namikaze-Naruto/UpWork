# Dublin Diocese Parish Data Extraction - Project Report

**Date:** 2025-12-19
**Project:** Dublin Diocese Parish Data Extraction

## 1. Project Overview
The goal of this project was to manually-quality scrape data for all parishes listed on the Dublin Diocese "Parishes A-Z" directory (`https://www.dublindiocese.ie/parishes-mass-times/parishes-a-z/`). The extraction prioritized accuracy and completeness, capturing fields often missed by automated tools.

## 2. Deliverables
The project is organized into the following folder structure:

-   **Output/**: Contains the final deliverables.
    -   `dublin_parishes.csv`: The complete dataset.
    -   `Project_Report.md`: This document.
-   **Input/**: Contains the source code.
    -   `script.py`: The Python script used to perform the extraction.
-   **Processing/**: Contains execution logs.
    -   `extraction_log.txt`: Detailed log of the scraping process.

## 3. Data Statistics
-   **Total Parishes Extracted**: 197
-   **Format**: Colon-Separated Values (`:`) to accommodate commas within address fields.
-   **Columns**:
    1.  `Parish Name`
    2.  `Church Names` (Pipe `|` separated if multiple)
    3.  `Priests` (Pipe `|` separated)
    4.  `Secretary`
    5.  `Phone` (Pipe `|` separated)
    6.  `Email` (Pipe `|` separated)
    7.  `Address` (Pipe `|` separated)
    8.  `Parish URL`

## 4. Methodology
A custom Python script was developed using `requests` and `BeautifulSoup` to:
1.  **Iterate** through the main directory to identify all unique parish URLs.
2.  **Visit** each parish page individually.
3.  **Parse** specific HTML elements to extract contact details, personnel, and church names.
4.  **Clean** the data by removing generic headers (e.g., "Church Information", "Contact") and formatting phone/email fields.
5.  **Validate** input by adhering to a specific schema and handling exceptions gracefully.

## 5. Usage
To re-run the extraction:
1.  Navigate to the `Input` directory: `cd Input`
2.  Run the script: `python script.py`
3.  The output file in `Output/dublin_parishes.csv` will be correctly overwritten.

## 6. Verification
Spot checks were performed on random parishes (e.g., Ardlea, Arklow, Avoca) to ensure that:
-   Multiple churches were captured correctly.
-   Phone numbers and emails were formatted cleanly.
-   The colon separator effectively handled addresses containing commas.
