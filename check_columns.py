"""Quick script to check actual columns in EDC metrics files"""
import sys
sys.path.append('src')

from ingestion.data_loader import DataIngestionEngine

# Load data
engine = DataIngestionEngine()
all_data = engine.ingest_all_studies()

# Check first study with EDC data
for study_name, study_data in all_data.items():
    if "edc_metrics" in study_data:
        edc_df = study_data["edc_metrics"]
        print(f"\n{'='*60}")
        print(f"Study: {study_name}")
        print(f"{'='*60}")
        print(f"Shape: {edc_df.shape}")
        print(f"\nColumn Names:")
        for i, col in enumerate(edc_df.columns, 1):
            print(f"  {i}. {col}")
        
        print(f"\nSample Data (first 2 rows):")
        print(edc_df.head(2).to_string())
        
        print(f"\nColumn Data Types:")
        print(edc_df.dtypes)
        
        print(f"\nBasic Statistics:")
        print(edc_df.describe())
        
        # Only check first study
        break
