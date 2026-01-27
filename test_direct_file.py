"""Test reading Study 6 EDC file directly"""
import pandas as pd
from pathlib import Path

file_path = Path("Data/Study 6 _CPID_Input Files - Anonymization/CPID_EDC_Metrics_URSV2.0_updated.xlsx")

if not file_path.exists():
    print(f"File not found: {file_path}")
    exit(1)

# Read raw Excel file
raw_df = pd.read_excel(file_path, header=None, engine='openpyxl')

print(f"Raw shape: {raw_df.shape}")
print(f"\nRow 0 (main headers): {list(raw_df.iloc[0, :15])}")
print(f"\nRow 1 (sub headers): {list(raw_df.iloc[1, :15])}")
print(f"\nRow 2 (detail headers): {list(raw_df.iloc[2, :15])}")

# Combine headers as the parser does
columns = []
for i in range(raw_df.shape[1]):
    parts = []
    for row_idx in [0, 1, 2]:
        val = raw_df.iloc[row_idx, i]
        if pd.notna(val) and str(val).strip():
            parts.append(str(val).strip())
    
    if parts:
        col_name = ' '.join(parts)
    else:
        col_name = f'Column_{i}'
    
    columns.append(col_name)

print(f"\nTotal columns: {len(columns)}")
print(f"\nFirst 20 column names:")
for idx, col in enumerate(columns[:20]):
    print(f"  {idx}: {col}")

# Check for query columns
query_cols = [col for col in columns if 'quer' in col.lower() or 'total' in col.lower()]
print(f"\nQuery-related columns found: {len(query_cols)}")
for col in query_cols:
    print(f"  - {col}")
