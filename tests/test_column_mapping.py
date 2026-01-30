import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import COLUMN_MAPPINGS
from ingestion.data_loader import DataIngestionEngine

# Test column mapping
test_columns = ['#Total Queries', '# Site Queries', 'Input files - Missing Visits', 'Missing Page']

print("Testing column mapping logic:")
print("="*80)

for col in test_columns:
    col_stripped = str(col).strip()
    matched = False
    matched_to = None
    
    for standard_name, variations in COLUMN_MAPPINGS.items():
        for variation in variations:
            if variation.lower() in col_stripped.lower() or col_stripped.lower() in variation.lower():
                matched = True
                matched_to = standard_name
                break
        if matched:
            break
    
    print(f"Column: '{col}'")
    print(f"  Matched: {matched}")
    print(f"  Maps to: {matched_to}")
    print()

# Now test with actual Study 6 data
print("\n" + "="*80)
print("Testing with actual Study 6 data:")
print("="*80)

engine = DataIngestionEngine(data_directory=Path(r"C:\Users\Ayan Parmar\Desktop\NestTry\data"))
studies = engine.discover_studies()
study6 = [s for s in studies if "Study 6" in s][0]
study_dir = Path(r"C:\Users\Ayan Parmar\Desktop\NestTry\data") / study6

data = engine.ingest_study_data(study_dir)
edc_df = data['edc_metrics']

print(f"\nOriginal columns ({len(edc_df.columns)}):")
print([col for col in edc_df.columns if 'quer' in col.lower() or 'missing' in col.lower()])

# Apply standardization
renamed_cols = {}
for standard_name, variations in COLUMN_MAPPINGS.items():
    for col in edc_df.columns:
        col_stripped = str(col).strip()
        for variation in variations:
            if variation.lower() in col_stripped.lower() or col_stripped.lower() in variation.lower():
                if col not in renamed_cols:
                    renamed_cols[col] = standard_name
                    print(f"  '{col}' -> '{standard_name}'")
                break
        if col in renamed_cols:
            break

edc_df_renamed = edc_df.rename(columns=renamed_cols)

print(f"\nAfter standardization ({len(edc_df_renamed.columns)}):")
print([col for col in edc_df_renamed.columns if 'quer' in col.lower() or 'missing' in col.lower()])

# Check if open_queries exists and has data
if 'open_queries' in edc_df_renamed.columns:
    print(f"\n✓ open_queries column exists!")
    print(f"  Non-zero values: {(edc_df_renamed['open_queries'] > 0).sum()}")
    print(f"  Total: {edc_df_renamed['open_queries'].sum()}")
    print(f"  Max: {edc_df_renamed['open_queries'].max()}")
else:
    print("\n✗ open_queries column NOT FOUND after standardization!")
    print("Available columns:", list(edc_df_renamed.columns))
