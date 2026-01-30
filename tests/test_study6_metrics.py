import pandas as pd
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ingestion.data_loader import DataIngestionEngine
from harmonization.canonical_model import CanonicalDataModel
from metrics.metrics_engine import MetricsEngine

# Initialize the engine
engine = DataIngestionEngine(data_directory=Path(r"C:\Users\Ayan Parmar\Desktop\NestTry\data"))

# Find Study 6
studies = engine.discover_studies()
study6 = [s for s in studies if "Study 6" in s][0]
study_dir = Path(r"C:\Users\Ayan Parmar\Desktop\NestTry\data") / study6

print(f"Study: {study6}")
print("="*80)

# Ingest the data
data = engine.ingest_study_data(study_dir)

# Get EDC metrics
edc_data = data['edc_metrics']
print(f"\nEDC Metrics - {len(edc_data)} rows")
print(f"Columns: {list(edc_data.columns)}")

# Check for query columns
query_cols = [col for col in edc_data.columns if 'quer' in col.lower()]
print(f"\nQuery columns found: {query_cols}")

for col in query_cols:
    print(f"\n{col} statistics:")
    print(f"  Min: {edc_data[col].min()}")
    print(f"  Max: {edc_data[col].max()}")
    print(f"  Mean: {edc_data[col].mean():.2f}")
    print(f"  Subjects with >0: {(edc_data[col] > 0).sum()}")

# Now harmonize
print("\n" + "="*80)
print("HARMONIZATION")
print("="*80)

cdm = CanonicalDataModel()
ingested_studies = {study6: data}
canonical_model = cdm.build_canonical_model(ingested_studies)

# Get subjects
subjects_df = canonical_model['subjects']
print(f"\nSubjects DataFrame - {len(subjects_df)} rows")
print(f"Columns: {list(subjects_df.columns)}")

# Check for harmonized query columns
query_cols = [col for col in subjects_df.columns if 'quer' in col.lower()]
print(f"\nQuery columns after harmonization: {query_cols}")

for col in query_cols:
    print(f"\n{col} statistics:")
    print(f"  Type: {subjects_df[col].dtype}")
    print(f"  Min: {subjects_df[col].min()}")
    print(f"  Max: {subjects_df[col].max()}")
    print(f"  Non-null count: {subjects_df[col].notna().sum()}")
    print(f"  Subjects with >0: {(subjects_df[col] > 0).sum()}")

# Now calculate metrics
print("\n" + "="*80)
print("METRICS CALCULATION")
print("="*80)

metrics_engine = MetricsEngine()
study_entity = canonical_model['studies'].iloc[0]

# Calculate metrics
metrics = metrics_engine.calculate_all_metrics_for_study(
    study_entity,
    canonical_model['sites'],
    subjects_df,
    canonical_model['queries'],
    canonical_model['safety_events']
)

print(f"\nMetrics calculated:")
print(f"  Total subjects: {metrics.get('total_subjects', 'N/A')}")
print(f"  Clean patients: {metrics.get('clean_patients', 'N/A')}")
print(f"  Clean patient %: {metrics.get('clean_patient_percentage', 'N/A')}")
print(f"  Open queries: {metrics.get('open_queries', 'N/A')}")

# Check clean patient logic
print("\n" + "="*80)
print("CLEAN PATIENT ASSESSMENT")
print("="*80)

# Manually check assess_clean_patient_status
clean_flags = metrics_engine.assess_clean_patient_status(subjects_df)
print(f"\nClean patient flags - {len(clean_flags)} total")
print(f"  Clean (True): {clean_flags.sum()}")
print(f"  Not clean (False): {(~clean_flags).sum()}")

# Show some subjects that should not be clean
print("\nSubjects with queries (should NOT be clean):")
subjects_with_queries = subjects_df[subjects_df.get('open_queries', pd.Series([0]*len(subjects_df))) > 0]
if len(subjects_with_queries) > 0:
    print(f"  Found {len(subjects_with_queries)} subjects with queries")
    print(subjects_with_queries[['subject_id', 'open_queries', 'site_id']].head())
    print(f"  Their clean flags: {clean_flags[subjects_with_queries.index].tolist()}")
else:
    print("  No subjects found with open_queries > 0 !")
    print("  Checking raw #Total Queries column...")
    if '#Total Queries' in subjects_df.columns:
        with_queries = subjects_df[subjects_df['#Total Queries'] > 0]
        print(f"  Found {len(with_queries)} subjects with #Total Queries > 0")
        if len(with_queries) > 0:
            print(with_queries[['subject_id', '#Total Queries', 'site_id']].head())
