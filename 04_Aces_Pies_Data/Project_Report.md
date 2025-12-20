# Project Report: ACES & PIES Data Conversion

## Project Overview
**Objective**: Convert manufacturer product data from ACES (Aftermarket Catalog Exchange Standard) and PIES (Product Information Exchange Standard) XML formats into a flattened, easy-to-use Excel/CSV format for e-commerce listing (e.g., eBay).

## Methodology
The solution was implemented using a custom Python script that parses the complex XML structures and flattens them into a tabular format.

### Workflow
1.  **Input Analysis**:
    -   Source files identified as standard AutoCare XML (`.xml`).
    -   PIES files contained product attributes, descriptions, and digital assets.
    -   ACES files contained vehicle fitment data (application mapping).

2.  **Data Processing (`src/convert_data.py`)**:
    -   **Parsing**: Used `xml.etree.ElementTree` to traverse the XML nodes.
    -   **Flattening**: Converted nested Key-Value pairs (e.g., specific Product Attributes) into distinct columns (e.g., `Attribute_Material`, `Attribute_Color`).
    -   **Filtering**:
        -   Filtered Descriptions and Attributes to **English ('EN')** only.
        -   Removed redundant columns (foreign languages).
        -   Dropped entirely empty columns to ensure a clean dataset.
    -   **Merging**: Joined PIES product data with ACES vehicle fitment string based on `PartNumber`.

3.  **Output Generation**:
    -   Generated `Consolidated_Catalog.csv` for high-volume data compatibility.
    -   Generated `Consolidated_Catalog.xlsx` for easy viewing.

## Deliverables
**Location**: `d:\UpWork\04_Aces_Pies_Data\Output\`

| File Name | Description |
| :--- | :--- |
| **Consolidated_Catalog.csv** | The primary master file. Contains all products, flattened attributes, and comma-separated vehicle IDs. |
| **Consolidated_Catalog.xlsx** | Excel version of the master file. |

## Data Structure Summary
The final output contains the following key sections:
-   **Identity**: `PartNumber`, `Brand`
-   **Content**: `Description`, `Features` (Marketing Bullet Points)
-   **Attributes**: Dynamic columns like `Attribute_Housing_Color`, `Attribute_Material`, etc.
-   **Media**: `Images` (semicolon-separated filenames)
-   **Fitment**: `VehicleIDs` (comma-separated ACES IDs)

## Usage
To run the conversion on new data:
1.  Place new XML/Zip files in the `Input` folder.
2.  Run the script:
    ```powershell
    python d:\UpWork\04_Aces_Pies_Data\Processing\convert_data.py
    ```
3.  Collect results from the `Output` folder.
