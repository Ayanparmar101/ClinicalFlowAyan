import pandas as pd
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ingestion.data_loader import DataIngestionEngine

# Initialize the engine
engine = DataIngestionEngine(data_directory=Path(r"C:\Users\Ayan Parmar\Desktop\NestTry\data"))

# Find Study 6
studies = engine.discover_studies()
study6 = [s for s in studies if "Study 6" in s][0]

print(f"Study: {study6}")
study_dir = Path(r"C:\Users\Ayan Parmar\Desktop\NestTry\data") / study6
print(f"Directory: {study_dir}")
print("\nIngesting Study 6 data...")

# Ingest the data
data = engine.ingest_study_data(study_dir)

# Check each file type
for file_type, df in data.items():
    if df is not None and not df.empty:
        print(f"\n{'='*80}")
        print(f"File type: {file_type}")
        print(f"Shape: {df.shape}")
        print(f"Columns ({len(df.columns)}): {list(df.columns)}")
        if 'edc_metrics' in file_type or 'metrics' in file_type:
            print("\nFirst few rows:")
            print(df.head(3))
            print("\nData types:")
            print(df.dtypes)
            # Check for query-related columns
            query_cols = [col for col in df.columns if 'quer' in col.lower() or 'lnr' in col.lower() or 'issue' in col.lower()]
            if query_cols:
                print(f"\nQuery-related columns found: {query_cols}")
                for col in query_cols:
                    print(f"\n{col} - Sample values:")
                    print(df[col].value_counts())
            else:
                print("\nNo query-related columns found!")
