import pandas as pd
import openpyxl

# Check Study 6 EDC Metrics file
file_path = r"data\Study 6 _CPID_Input Files - Anonymization\CPID_EDC_Metrics_URSV2.0_updated.xlsx"

# Read with openpyxl to see the raw structure
wb = openpyxl.load_workbook(file_path)
sheet = wb.active

print("=" * 80)
print(f"Checking: {file_path}")
print("=" * 80)

# Get the three header rows
header_row1 = [cell.value for cell in sheet[1]]
header_row2 = [cell.value for cell in sheet[2]]
header_row3 = [cell.value for cell in sheet[3]]

print("\nFirst 20 column headers (combined):")
for i in range(min(20, len(header_row1))):
    h1 = str(header_row1[i]) if header_row1[i] else ""
    h2 = str(header_row2[i]) if header_row2[i] else ""
    h3 = str(header_row3[i]) if header_row3[i] else ""
    combined = " ".join([h1, h2, h3]).strip()
    print(f"  Column {i}: {combined}")

# Read the actual data using pandas
from src.ingestion.data_loader import DataLoader
loader = DataLoader()
df = loader._load_edc_metrics_file(file_path)

print(f"\n\nDataFrame shape: {df.shape}")
print("\nColumn names:")
for col in df.columns[:20]:
    print(f"  - {col}")

# Check for missing visits and missing pages columns
missing_visit_cols = [col for col in df.columns if 'missing' in col.lower() and 'visit' in col.lower()]
missing_page_cols = [col for col in df.columns if 'missing' in col.lower() and 'page' in col.lower()]

print(f"\n\nMissing Visits columns found: {missing_visit_cols}")
print(f"Missing Pages columns found: {missing_page_cols}")

if missing_visit_cols:
    col = missing_visit_cols[0]
    print(f"\n'{col}' column data:")
    print(f"  Data type: {df[col].dtype}")
    print(f"  Unique values: {df[col].unique()[:20]}")
    print(f"  Value counts:\n{df[col].value_counts()}")
    print(f"  Stats: min={df[col].min()}, max={df[col].max()}, mean={df[col].mean()}")

if missing_page_cols:
    col = missing_page_cols[0]
    print(f"\n'{col}' column data:")
    print(f"  Data type: {df[col].dtype}")
    print(f"  Unique values: {df[col].unique()[:20]}")
    print(f"  Value counts:\n{df[col].value_counts()}")
    print(f"  Stats: min={df[col].min()}, max={df[col].max()}, mean={df[col].mean()}")

# Show first few rows of data
print("\n\nFirst 5 rows of relevant columns:")
relevant_cols = ['Subject ID', 'Input files - Missing Visits', 'Missing Page', '#Total Queries']
available_cols = [col for col in relevant_cols if col in df.columns]
if available_cols:
    print(df[available_cols].head())
else:
    print("Columns not found. Showing first 5 rows of first 10 columns:")
    print(df.iloc[:, :10].head())
