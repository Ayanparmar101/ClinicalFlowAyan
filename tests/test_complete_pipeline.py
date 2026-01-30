"""
Comprehensive test of the complete data pipeline
"""
import sys
from pathlib import Path
sys.path.insert(0, 'src')

from ingestion.data_loader import DataIngestionEngine
from harmonization.canonical_model import CanonicalDataModel
from metrics.metrics_engine import MetricsEngine
from metrics.dqi_calculator import DataQualityIndex

print("="*80)
print("COMPREHENSIVE PIPELINE TEST")
print("="*80)

# Step 1: Data Ingestion
print("\n1. DATA INGESTION")
print("-"*80)
ingestion_engine = DataIngestionEngine(Path('data'))
studies = ingestion_engine.discover_studies()
print(f"✓ Discovered {len(studies)} studies")

all_data = {}
for study_name in studies[:3]:  # Test first 3 studies
    study_df = ingestion_engine.load_study_data(study_name)
    if study_df is not None and not study_df.empty:
        all_data[study_name] = study_df
        print(f"✓ Loaded {study_name}: {len(study_df)} subjects")
        print(f"  Columns: {list(study_df.columns)}")
        print(f"  Missing visits: {study_df['missing_visits'].sum()}")
        print(f"  Missing pages: {study_df['missing_pages'].sum()}")
        print(f"  Open queries: {study_df['open_queries'].sum()}")

# Step 2: Harmonization
print("\n2. HARMONIZATION")
print("-"*80)
canonical_model = CanonicalDataModel()
canonical_entities = canonical_model.build_canonical_model(all_data)
print(f"✓ Built canonical model")
for entity_name, entity_df in canonical_entities.items():
    if not entity_df.empty:
        print(f"  {entity_name}: {len(entity_df)} records")

# Step 3: Metrics Calculation
print("\n3. METRICS CALCULATION")
print("-"*80)
metrics_engine = MetricsEngine(canonical_entities, all_data)
all_metrics = {}

for study_name in all_data.keys():
    print(f"\nProcessing {study_name}:")
    study_metrics = metrics_engine.calculate_all_metrics_for_study(study_name)
    all_metrics[study_name] = study_metrics
    
    if "subject_metrics" in study_metrics:
        subject_df = study_metrics["subject_metrics"]
        print(f"  ✓ Subject metrics: {len(subject_df)} subjects")
        
        # Check completeness metrics
        if "pct_missing_visits" in subject_df.columns:
            print(f"    Missing visits %: mean={subject_df['pct_missing_visits'].mean():.1f}%, max={subject_df['pct_missing_visits'].max():.1f}%")
        if "pct_missing_pages" in subject_df.columns:
            print(f"    Missing pages %: mean={subject_df['pct_missing_pages'].mean():.1f}%, max={subject_df['pct_missing_pages'].max():.1f}%")
        
        # Check query metrics
        if "open_queries" in subject_df.columns:
            print(f"    Open queries: total={subject_df['open_queries'].sum()}, avg={subject_df['open_queries'].mean():.1f}")
    
    # Check site metrics
    if "site_metrics" in study_metrics:
        site_df = study_metrics["site_metrics"]
        if not site_df.empty:
            print(f"  ✓ Site metrics: {len(site_df)} sites")
            print(f"    Avg performance score: {site_df['performance_score'].mean():.1f}")
        else:
            print(f"  ⚠ Site metrics: EMPTY")
    else:
        print(f"  ⚠ Site metrics: NOT FOUND")
    
    # Check safety metrics
    if "safety_metrics" in study_metrics:
        safety = study_metrics["safety_metrics"]
        print(f"  ✓ Safety metrics: {safety['total_saes']} SAEs")

# Step 4: DQI Calculation
print("\n4. DQI CALCULATION")
print("-"*80)
dqi_calculator = DataQualityIndex()
for study_name, metrics in all_metrics.items():
    if "subject_metrics" in metrics:
        metrics["subject_metrics"] = dqi_calculator.calculate_subject_dqi(
            metrics["subject_metrics"]
        )
        dqi_scores = metrics["subject_metrics"]["dqi_score"]
        print(f"{study_name}: DQI mean={dqi_scores.mean():.1f}, min={dqi_scores.min():.1f}, max={dqi_scores.max():.1f}")

print("\n" + "="*80)
print("PIPELINE TEST COMPLETE ✓")
print("="*80)
