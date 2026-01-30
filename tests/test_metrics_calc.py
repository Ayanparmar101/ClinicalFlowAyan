"""Test metrics calculation with real data"""
import pandas as pd
import sys
from pathlib import Path
sys.path.append('src')

from ingestion.data_loader import DataIngestionEngine
from metrics.metrics_engine import MetricsEngine

# Load real data for Study 6
loader = DataIngestionEngine(Path("Data"))
studies_data = loader.ingest_all_studies()

# Find Study 6
study_6 = None
for study_name, data in studies_data.items():
    if "Study 6" in study_name or "Study 6_" in study_name:
        study_6 = data
        print(f"Found study: {study_name}")
        break

if not study_6:
    print("Study 6 not found!")
    sys.exit(1)

# Get EDC metrics data
edc_data = study_6.get('edc_metrics')
if edc_data is None or edc_data.empty:
    print("No EDC metrics data found!")
    sys.exit(1)

print(f"\nOriginal EDC data shape: {edc_data.shape}")
print(f"Original columns: {list(edc_data.columns)[:10]}...")

# Initialize metrics engine
engine = MetricsEngine(studies_data)

# Standardize column names (this is what should happen in calculate_metrics)
standardized_df = engine.standardize_column_names(edc_data.copy())

print(f"\nStandardized columns: {list(standardized_df.columns)[:10]}...")

# Check if open_queries column exists
if 'open_queries' in standardized_df.columns:
    print(f"\n✅ SUCCESS: 'open_queries' column found!")
    print(f"Open queries stats:")
    print(f"  - Min: {standardized_df['open_queries'].min()}")
    print(f"  - Max: {standardized_df['open_queries'].max()}")
    print(f"  - Mean: {standardized_df['open_queries'].mean():.2f}")
    print(f"  - Total: {standardized_df['open_queries'].sum()}")
    print(f"  - Subjects with queries: {(standardized_df['open_queries'] > 0).sum()}")
else:
    print(f"\n❌ FAILED: 'open_queries' column NOT found!")
    print(f"Available columns: {list(standardized_df.columns)}")

# Check other expected columns
expected_cols = ['site_id', 'subject_id', 'missing_visits', 'missing_pages']
for col in expected_cols:
    if col in standardized_df.columns:
        print(f"✅ Found '{col}' column")
    else:
        print(f"❌ Missing '{col}' column")
