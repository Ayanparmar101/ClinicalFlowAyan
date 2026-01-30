"""Test the new data loading with proper header parsing"""
import sys
sys.path.append('src')

from ingestion.data_loader import DataIngestionEngine
import pandas as pd

print("="*80)
print("TESTING NEW DATA INGESTION WITH PROPER HEADER PARSING")
print("="*80)

engine = DataIngestionEngine()

# Test loading Study 17
print("\nLoading Study 17 data...")
all_data = engine.ingest_study_data("Study 17_CPID_Input Files - Anonymization")

if "edc_metrics" in all_data:
    edc_df = all_data["edc_metrics"]
    print(f"\nSUCCESS: Successfully loaded EDC metrics: {edc_df.shape}")
    
    print("\n" + "="*80)
    print("COLUMNS FOUND:")
    print("="*80)
    for i, col in enumerate(edc_df.columns, 1):
        print(f"{i:3}. {col}")
    
    print("\n" + "="*80)
    print("KEY METRICS COLUMNS:")
    print("="*80)
    metrics_cols = [col for col in edc_df.columns if any(keyword in col for keyword in ['Missing', 'Open', '#', 'Coded', 'issues'])]
    for col in metrics_cols:
        print(f"  - {col}")
    
    print("\n" + "="*80)
    print("SAMPLE DATA (first 3 rows, selected columns):")
    print("="*80)
    
    # Show key columns
    display_cols = ['Subject ID', 'Site ID'] + [col for col in metrics_cols[:5]]
    display_cols = [col for col in display_cols if col in edc_df.columns]
    if display_cols:
        print(edc_df[display_cols].head(3))
    
    print("\n" + "="*80)
    print("STATISTICS FOR KEY METRICS:")
    print("="*80)
    numeric_metrics = [col for col in metrics_cols if edc_df[col].dtype in ['int64', 'float64']]
    if numeric_metrics:
        stats = edc_df[numeric_metrics].describe()
        print(stats)
        
        print("\n" + "="*80)
        print("QUALITY INDICATORS:")
        print("="*80)
        for col in numeric_metrics[:6]:  # First 6 metrics
            total = edc_df[col].sum()
            mean = edc_df[col].mean()
            subjects_affected = (edc_df[col] > 0).sum()
            pct_affected = (subjects_affected / len(edc_df) * 100)
            print(f"\n{col}:")
            print(f"  Total: {total:.0f}")
            print(f"  Mean per subject: {mean:.2f}")
            print(f"  Subjects affected: {subjects_affected} ({pct_affected:.1f}%)")
else:
    print("\nERROR: EDC metrics not loaded!")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
