"""Test the new multi-file loader with Study 6"""
import sys
from pathlib import Path
sys.path.insert(0, 'src')

from ingestion.multi_file_loader import MultiFileDataLoader

loader = MultiFileDataLoader(Path('data'))

print("="*80)
print("TESTING MULTI-FILE LOADER WITH STUDY 6")
print("="*80)

df = loader.load_study_data('Study 6 _CPID_Input Files - Anonymization')

if df is not None:
    print(f"\n✓ Successfully loaded {len(df)} subjects")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nData types:")
    print(df.dtypes)
    print(f"\nFirst 3 subjects:")
    print(df.head(3).to_string())
    
    print("\n" + "="*80)
    print("MISSING VISITS ANALYSIS")
    print("="*80)
    print(f"Min: {df['missing_visits'].min()}")
    print(f"Max: {df['missing_visits'].max()}")
    print(f"Mean: {df['missing_visits'].mean():.2f}")
    print(f"Non-zero count: {(df['missing_visits'] > 0).sum()}")
    
    print("\n" + "="*80)
    print("MISSING PAGES ANALYSIS")
    print("="*80)
    print(f"Min: {df['missing_pages'].min()}")
    print(f"Max: {df['missing_pages'].max()}")
    print(f"Mean: {df['missing_pages'].mean():.2f}")
    print(f"Non-zero count: {(df['missing_pages'] > 0).sum()}")
    
    print("\n" + "="*80)
    print("QUERIES ANALYSIS")
    print("="*80)
    print(f"Min: {df['open_queries'].min()}")
    print(f"Max: {df['open_queries'].max()}")
    print(f"Mean: {df['open_queries'].mean():.2f}")
    print(f"Non-zero count: {(df['open_queries'] > 0).sum()}")
    
    print("\n" + "="*80)
    print("SAMPLE SUBJECTS WITH DATA")
    print("="*80)
    subjects_with_data = df[
        (df['missing_visits'] > 0) | 
        (df['missing_pages'] > 0) | 
        (df['open_queries'] > 0)
    ]
    print(f"Subjects with any issues: {len(subjects_with_data)}")
    if len(subjects_with_data) > 0:
        print("\nFirst 5:")
        print(subjects_with_data.head(5)[['subject_id', 'missing_visits', 'missing_pages', 'open_queries']].to_string())
else:
    print("❌ Failed to load data")
