"""Debug the parser to see where columns are being lost"""
import pandas as pd
import numpy as np
from pathlib import Path

file_path = Path("Data/Study 6 _CPID_Input Files - Anonymization/CPID_EDC_Metrics_URSV2.0_updated.xlsx")

# Read raw data
raw_df = pd.read_excel(file_path, header=None, engine='openpyxl')

print(f"Raw DF shape: {raw_df.shape}")

# Extract header rows
header_row1 = raw_df.iloc[0].fillna('')
header_row2 = raw_df.iloc[1].fillna('')
header_row3 = raw_df.iloc[2].fillna('')

print(f"Header row 1 length: {len(header_row1)}")
print(f"Header row 2 length: {len(header_row2)}")
print(f"Header row 3 length: {len(header_row3)}")

# Build column names
columns = []
for i in range(len(header_row1)):
    h1 = str(header_row1.iloc[i]).strip()
    h2 = str(header_row2.iloc[i]).strip()
    h3 = str(header_row3.iloc[i]).strip()
    
    parts = [p for p in [h1, h2, h3] if p and p != 'nan' and p != '']
    
    if parts:
        col_name = ' - '.join(parts) if len(parts) > 1 else parts[0]
    else:
        col_name = f'Column_{i}'
    
    columns.append(col_name)

print(f"\nTotal columns created: {len(columns)}")

# Extract data
data_df = raw_df.iloc[3:].copy()
data_df.columns = columns

print(f"\nData DF shape after setting columns: {data_df.shape}")

# Remove rows where key identifiers are missing
data_df = data_df.dropna(subset=[col for col in data_df.columns if 'Subject' in col or 'Site' in col], how='all')

print(f"After dropna subject/site: {data_df.shape}")

# Clean up: remove completely empty rows
data_df = data_df.replace('', np.nan)
data_df = data_df.dropna(how='all')

print(f"After dropna(how='all'): {data_df.shape}")

# Convert numeric columns
for col in data_df.columns:
    if any(keyword in col for keyword in ['Missing', '#', 'Open', 'Closed', 'Total', 'Count']):
        data_df[col] = pd.to_numeric(data_df[col], errors='coerce').fillna(0)

print(f"\nFinal shape: {data_df.shape}")
print(f"\nFinal columns: {list(data_df.columns)}")

# Check for #Total Queries
if '#Total Queries' in data_df.columns:
    print(f"\n✅ '#Total Queries' column EXISTS")
    print(f"Values: {data_df['#Total Queries'].values[:10]}")
else:
    print(f"\n❌ '#Total Queries' column MISSING")
    query_cols = [col for col in data_df.columns if 'quer' in col.lower()]
    print(f"Query columns found: {query_cols}")
