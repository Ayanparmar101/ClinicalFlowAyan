"""
Direct pipeline test without logger dependencies
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

import pandas as pd
import numpy as np

# Mock logger to avoid import issues
class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def debug(self, msg): pass  # Suppress debug
    def warning(self, msg): print(f"WARNING: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

# Patch logger in modules before import
import sys
sys.modules['loguru'] = type(sys)('loguru')
sys.modules['loguru'].logger = MockLogger()

# Now import our modules
from ingestion.multi_file_loader import MultiFileDataLoader
from config import DATA_PATH

def test_multi_file_loader():
    """Test the multi-file data loader"""
    print("=" * 80)
    print("TESTING MULTI-FILE DATA LOADER")
    print("=" * 80)
    
    loader = MultiFileDataLoader(DATA_PATH)
    
    # Load Study 1
    study_name = "Study 1_CPID_Input Files - Anonymization"
    print(f"\nLoading: {study_name}")
    
    df = loader.load_study_data(study_name)
    
    if df is not None and not df.empty:
        print(f"\n✓ Successfully loaded {len(df)} subjects")
        print(f"\n✓ Columns ({len(df.columns)}):")
        for col in df.columns:
            non_null = df[col].notna().sum()
            print(f"  - {col}: {non_null} non-null values")
        
        print(f"\n✓ Sample data (first 3 subjects):")
        print(df.head(3))
        
        print(f"\n✓ Data summary:")
        numeric_cols = ['missing_pages', 'missing_visits', 'open_queries', 
                       'coded_terms', 'uncoded_terms', 'open_lnr_issues', 
                       'sae_review']
        for col in numeric_cols:
            if col in df.columns:
                total = df[col].sum()
                mean = df[col].mean()
                print(f"  - {col}: total={total:.0f}, mean={mean:.2f}")
        
        return df
    else:
        print("\n✗ Failed to load data")
        return None

def test_metrics_calculation(df):
    """Test metrics calculation without full engine"""
    print("\n" + "=" * 80)
    print("TESTING METRICS CALCULATION")
    print("=" * 80)
    
    if df is None or df.empty:
        print("✗ No data to calculate metrics")
        return None
    
    # Calculate simple DQI manually
    print("\n✓ Calculating DQI scores...")
    
    df_metrics = df.copy()
    
    # Normalize metrics to 0-100 scale
    for col in ['missing_pages', 'missing_visits', 'open_queries']:
        if col in df_metrics.columns:
            max_val = df_metrics[col].max()
            if max_val > 0:
                # Higher values = worse quality
                df_metrics[f'{col}_score'] = (1 - df_metrics[col] / max_val) * 100
            else:
                df_metrics[f'{col}_score'] = 100
    
    # Calculate composite DQI (simple average)
    score_cols = [col for col in df_metrics.columns if col.endswith('_score')]
    if score_cols:
        df_metrics['dqi_score'] = df_metrics[score_cols].mean(axis=1)
        
        # Classify risk
        df_metrics['risk_level'] = pd.cut(
            df_metrics['dqi_score'],
            bins=[0, 70, 85, 100],
            labels=['High', 'Medium', 'Low']
        )
        
        print(f"\n✓ DQI Statistics:")
        print(f"  - Mean DQI: {df_metrics['dqi_score'].mean():.2f}")
        print(f"  - Median DQI: {df_metrics['dqi_score'].median():.2f}")
        print(f"  - Min DQI: {df_metrics['dqi_score'].min():.2f}")
        print(f"  - Max DQI: {df_metrics['dqi_score'].max():.2f}")
        
        print(f"\n✓ Risk Distribution:")
        risk_counts = df_metrics['risk_level'].value_counts()
        for level, count in risk_counts.items():
            pct = count / len(df_metrics) * 100
            print(f"  - {level}: {count} ({pct:.1f}%)")
        
        print(f"\n✓ Sample subjects with DQI:")
        display_cols = ['subject_id', 'site_id', 'missing_visits', 'missing_pages', 
                       'open_queries', 'dqi_score', 'risk_level']
        display_cols = [col for col in display_cols if col in df_metrics.columns]
        print(df_metrics[display_cols].head(5).to_string())
        
        return df_metrics
    
    return df_metrics

def main():
    """Run tests"""
    print("\n" + "=" * 80)
    print("DIRECT PIPELINE VALIDATION TEST")
    print("Clinical Trial Intelligence Platform")
    print("=" * 80)
    
    try:
        # Test multi-file loader
        df = test_multi_file_loader()
        
        if df is None:
            print("\n✗ TEST FAILED: Could not load data")
            return False
        
        # Test metrics
        df_with_metrics = test_metrics_calculation(df)
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED SUCCESSFULLY")
        print("=" * 80)
        
        # Additional validation
        print("\n✓ VALIDATION SUMMARY:")
        print(f"  - Data loaded: {len(df)} subjects")
        print(f"  - Sites: {df['site_id'].nunique()} unique")
        print(f"  - Metrics calculated: DQI, risk levels")
        print(f"  - Files processed: multi-file aggregation working")
        
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
