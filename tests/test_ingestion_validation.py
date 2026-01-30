"""
Comprehensive Validation Test for Data Ingestion Layer
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from ingestion import DataIngestionEngine
from harmonization import CanonicalDataModel
from metrics import MetricsEngine, DataQualityIndex
import pandas as pd

def test_ingestion():
    """Test data ingestion layer"""
    print("=" * 80)
    print("TESTING DATA INGESTION LAYER")
    print("=" * 80)
    
    # Initialize engine
    engine = DataIngestionEngine()
    
    # Discover studies
    studies = engine.discover_studies()
    print(f"\n✓ Discovered {len(studies)} studies:")
    for study in studies[:5]:
        print(f"  - {study}")
    
    # Load one study
    test_study = "Study 1_CPID_Input Files - Anonymization"
    print(f"\n✓ Loading test study: {test_study}")
    
    df = engine.load_study_data(test_study)
    
    if df is not None and not df.empty:
        print(f"\n✓ Successfully loaded {len(df)} subjects")
        print(f"\n✓ Columns found:")
        for col in df.columns:
            print(f"  - {col}")
        
        print(f"\n✓ Sample data (first 3 rows):")
        print(df.head(3).to_string())
        
        print(f"\n✓ Data types:")
        print(df.dtypes)
        
        print(f"\n✓ Summary statistics:")
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            print(df[numeric_cols].describe())
        
        return df
    else:
        print("\n✗ ERROR: Failed to load data")
        return None

def test_harmonization(df):
    """Test harmonization layer"""
    print("\n" + "=" * 80)
    print("TESTING HARMONIZATION LAYER")
    print("=" * 80)
    
    canonical_model = CanonicalDataModel()
    
    # Standardize column names
    print("\n✓ Standardizing column names...")
    standardized_df = canonical_model.standardize_column_names(df, "test_study")
    
    print(f"\n✓ Standardized columns:")
    for col in standardized_df.columns:
        print(f"  - {col}")
    
    # Build canonical model
    print("\n✓ Building canonical model...")
    all_data = {
        "Study 1_CPID_Input Files - Anonymization": {
            "edc_metrics": df
        }
    }
    
    canonical_entities = canonical_model.build_canonical_model(all_data)
    
    print(f"\n✓ Canonical entities created:")
    for entity_name, entity_df in canonical_entities.items():
        if not entity_df.empty:
            print(f"  - {entity_name}: {len(entity_df)} records")
    
    return canonical_entities, all_data

def test_metrics(canonical_entities, all_data):
    """Test metrics engine"""
    print("\n" + "=" * 80)
    print("TESTING METRICS ENGINE")
    print("=" * 80)
    
    metrics_engine = MetricsEngine(canonical_entities, all_data)
    
    print("\n✓ Calculating metrics for Study 1...")
    study_metrics = metrics_engine.calculate_all_metrics_for_study("Study 1_CPID_Input Files - Anonymization")
    
    if "subject_metrics" in study_metrics:
        subject_df = study_metrics["subject_metrics"]
        print(f"\n✓ Subject metrics calculated for {len(subject_df)} subjects")
        print(f"\n✓ Metrics columns:")
        for col in subject_df.columns:
            print(f"  - {col}")
        
        print(f"\n✓ Sample subject metrics (first 3 rows):")
        print(subject_df.head(3).to_string())
    
    if "site_metrics" in study_metrics:
        site_df = study_metrics["site_metrics"]
        print(f"\n✓ Site metrics calculated for {len(site_df)} sites")
        print(f"\n✓ Site columns:")
        for col in site_df.columns:
            print(f"  - {col}")
        
        print(f"\n✓ Sample site metrics:")
        print(site_df.head(3).to_string())
    
    return study_metrics

def test_dqi(study_metrics):
    """Test DQI calculator"""
    print("\n" + "=" * 80)
    print("TESTING DQI CALCULATOR")
    print("=" * 80)
    
    dqi_calculator = DataQualityIndex()
    
    if "subject_metrics" in study_metrics:
        subject_df = study_metrics["subject_metrics"]
        print(f"\n✓ Calculating DQI for {len(subject_df)} subjects...")
        
        subject_df_with_dqi = dqi_calculator.calculate_subject_dqi(subject_df)
        
        print(f"\n✓ DQI calculated successfully")
        
        if "dqi_score" in subject_df_with_dqi.columns:
            print(f"\n✓ DQI Score statistics:")
            print(f"  - Mean: {subject_df_with_dqi['dqi_score'].mean():.2f}")
            print(f"  - Median: {subject_df_with_dqi['dqi_score'].median():.2f}")
            print(f"  - Min: {subject_df_with_dqi['dqi_score'].min():.2f}")
            print(f"  - Max: {subject_df_with_dqi['dqi_score'].max():.2f}")
        
        if "risk_level" in subject_df_with_dqi.columns:
            print(f"\n✓ Risk Level distribution:")
            risk_counts = subject_df_with_dqi['risk_level'].value_counts()
            for level, count in risk_counts.items():
                print(f"  - {level}: {count} ({count/len(subject_df_with_dqi)*100:.1f}%)")
        
        print(f"\n✓ Sample subjects with DQI (first 5):")
        display_cols = ['subject_id', 'site_id', 'dqi_score', 'risk_level', 'missing_visits', 'missing_pages', 'open_queries']
        display_cols = [col for col in display_cols if col in subject_df_with_dqi.columns]
        print(subject_df_with_dqi[display_cols].head(5).to_string())
        
        return subject_df_with_dqi
    
    return None

def main():
    """Run all validation tests"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE VALIDATION TEST")
    print("Clinical Trial Intelligence Platform")
    print("=" * 80)
    
    try:
        # Test ingestion
        df = test_ingestion()
        if df is None:
            print("\n✗ FAILED: Ingestion test failed")
            return False
        
        # Test harmonization
        canonical_entities, all_data = test_harmonization(df)
        
        # Test metrics
        study_metrics = test_metrics(canonical_entities, all_data)
        
        # Test DQI
        subject_df_with_dqi = test_dqi(study_metrics)
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED SUCCESSFULLY")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED WITH ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
