"""Test with multiple studies to see variation"""
import sys
sys.path.append('src')

from ingestion.data_loader import DataIngestionEngine
import pandas as pd

engine = DataIngestionEngine()

print("="*80)
print("TESTING MULTIPLE STUDIES FOR DATA VARIATION")
print("="*80)

studies_to_test = [
    "Study 1_CPID_Input Files - Anonymization",
    "Study 4_CPID_Input Files - Anonymization", 
    "Study 17_CPID_Input Files - Anonymization"
]

for study_name in studies_to_test:
    print(f"\n{'='*80}")
    print(f"STUDY: {study_name}")
    print('='*80)
    
    data = engine.ingest_study_data(study_name)
    
    if "edc_metrics" in data:
        edc_df = data["edc_metrics"]
        print(f"Shape: {edc_df.shape}")
        
        # Key quality columns
        quality_cols = [
            'Input files - Missing Visits', 'Missing Page', '#Total Queries',
            '# Uncoded Terms', '# Open issues in LNR', 'Inactivated forms and folders'
        ]
        
        available_cols = [col for col in quality_cols if col in edc_df.columns]
        
        print(f"\nQUALITY METRICS SUMMARY:")
        print("-" * 80)
        for col in available_cols:
            total = edc_df[col].sum()
            mean = edc_df[col].mean()
            max_val = edc_df[col].max()
            affected = (edc_df[col] > 0).sum()
            pct = (affected / len(edc_df) * 100) if len(edc_df) > 0 else 0
            
            print(f"\n{col}:")
            print(f"  Total: {total:8.0f}  |  Mean: {mean:6.2f}  |  Max: {max_val:6.0f}")
            print(f"  Subjects with issues: {affected}/{len(edc_df)} ({pct:.1f}%)")
    else:
        print("NO EDC METRICS FOUND")

print("\n" + "="*80)
print("COMPLETE")
print("="*80)
