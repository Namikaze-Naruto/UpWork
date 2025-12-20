
import pandas as pd
import os

file_path = r"d:\UpWork\04_Aces_Pies_Data\Consolidated_Data.xlsx"

if not os.path.exists(file_path):
    print("Error: File not found.")
    exit(1)

try:
    df = pd.read_excel(file_path)
    print(f"File loaded successfully. Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print("\nSample Data:")
    print(df[['PartNumber', 'Brand', 'Compatibility']].head().to_string())
    
    # Check for empty fitment
    empty_fitment = df['Compatibility'].isna().sum()
    print(f"\nRows with empty compatibility: {empty_fitment}")
    
except Exception as e:
    print(f"Verification Failed: {e}")
