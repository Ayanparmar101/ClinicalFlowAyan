"""
Analyze file structures across all studies to understand data format
"""
import pandas as pd
from pathlib import Path
import openpyxl

data_dir = Path('data')

file_patterns = {
    'missing_pages': 'Global_Missing_Pages_Report',
    'missing_visits': 'Visit Projection Tracker',
    'sae': 'eSAE Dashboard',
    'coding_meddra': 'GlobalCodingReport_MedDRA',
    'coding_whodd': 'GlobalCodingReport_WHODD',
    'inactivated': 'Inactivated forms',
    'edrr': 'Compiled_EDRR',
    'lab': 'Missing_Lab_Name'
}

print("="*80)
print("ANALYZING FILE STRUCTURES ACROSS ALL STUDIES")
print("="*80)

studies = [d for d in data_dir.iterdir() if d.is_dir() and d.name.startswith('Study')]

for file_type, pattern in file_patterns.items():
    print(f"\n{'='*80}")
    print(f"FILE TYPE: {file_type} (pattern: {pattern})")
    print('='*80)
    
    found_count = 0
    for study in sorted(studies)[:3]:  # Check first 3 studies
        matching_files = list(study.glob(f'*{pattern}*.xlsx'))
        if matching_files:
            found_count += 1
            file_path = matching_files[0]
            print(f"\n{study.name}: {file_path.name}")
            
            try:
                df = pd.read_excel(file_path, nrows=5)
                print(f"  Shape: {df.shape}")
                print(f"  Columns: {list(df.columns)}")
                print(f"  Sample row 0:")
                print(f"    {dict(df.iloc[0])}")
            except Exception as e:
                print(f"  ERROR: {e}")
    
    print(f"\nFound in {found_count}/{min(3, len(studies))} studies checked")

print("\n" + "="*80)
print("KEY INSIGHTS")
print("="*80)
print("""
Based on file analysis:
1. Missing Pages: Subject-level data with visit dates
2. Missing Visits: Projected visits with outstanding days
3. SAE: Discrepancy/issue tracking
4. Coding: Term coding status
5. EDRR: Issue counts per subject

Next step: Build unified subject-level aggregator
""")
