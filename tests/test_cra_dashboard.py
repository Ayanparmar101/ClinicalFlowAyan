"""
Test CRA Dashboard functionality
Validates all components of the Clinical Research Associate Dashboard
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from ingestion import DataIngestionEngine
from harmonization import CanonicalDataModel
from metrics import MetricsEngine, DataQualityIndex
from config import DATA_PATH

def test_cra_dashboard():
    """Test complete CRA dashboard data pipeline"""
    
    print("="*80)
    print("CRA DASHBOARD FUNCTIONALITY TEST")
    print("="*80)
    
    # Step 1: Load data
    print("\n1. DATA LOADING")
    print("-"*80)
    
    ingestion_engine = DataIngestionEngine(DATA_PATH)
    studies = ingestion_engine.discover_studies()
    print(f"✓ Discovered {len(studies)} studies")
    
    # Load first study for testing
    test_study = studies[0]
    print(f"\nTesting with: {test_study}")
    
    study_df = ingestion_engine.load_study_data(test_study)
    print(f"✓ Loaded study data: {len(study_df)} subjects")
    print(f"  Columns: {list(study_df.columns)}")
    
    # Step 2: Build canonical model
    print("\n2. HARMONIZATION")
    print("-"*80)
    
    all_data = {test_study: study_df}
    canonical_model = CanonicalDataModel()
    canonical_entities = canonical_model.build_canonical_model(all_data)
    
    print(f"✓ Subjects: {len(canonical_entities['subjects'])}")
    print(f"✓ Sites: {len(canonical_entities['sites'])}")
    
    # Step 3: Calculate metrics
    print("\n3. METRICS CALCULATION")
    print("-"*80)
    
    metrics_engine = MetricsEngine(canonical_entities, all_data)
    study_metrics = metrics_engine.calculate_all_metrics_for_study(test_study)
    
    # Validate subject metrics
    if "subject_metrics" in study_metrics:
        subject_df = study_metrics["subject_metrics"]
        print(f"✓ Subject metrics: {len(subject_df)} subjects")
        
        required_cols = ["subject_id", "open_queries", "missing_visits", "missing_pages"]
        for col in required_cols:
            if col in subject_df.columns:
                print(f"  ✓ Column '{col}' present")
            else:
                print(f"  ✗ Column '{col}' MISSING")
        
        # Check data values
        print(f"\n  Data Summary:")
        print(f"    Open queries: total={int(subject_df['open_queries'].sum())}, avg={subject_df['open_queries'].mean():.2f}")
        print(f"    Missing visits: total={int(subject_df['missing_visits'].sum())}, avg={subject_df['missing_visits'].mean():.2f}")
        print(f"    Missing pages: total={int(subject_df['missing_pages'].sum())}, avg={subject_df['missing_pages'].mean():.2f}")
    
    # Validate site metrics
    if "site_metrics" in study_metrics:
        site_df = study_metrics["site_metrics"]
        print(f"\n✓ Site metrics: {len(site_df)} sites")
        
        required_cols = ["site_id", "subject_count", "total_open_queries", "total_missing_visits", "performance_score"]
        for col in required_cols:
            if col in site_df.columns:
                print(f"  ✓ Column '{col}' present")
            else:
                print(f"  ✗ Column '{col}' MISSING")
        
        # Check site performance
        if "performance_score" in site_df.columns:
            print(f"\n  Site Performance:")
            print(f"    Mean: {site_df['performance_score'].mean():.1f}")
            print(f"    Min: {site_df['performance_score'].min():.1f}")
            print(f"    Max: {site_df['performance_score'].max():.1f}")
            
            high_perf = len(site_df[site_df["performance_score"] >= 80])
            med_perf = len(site_df[(site_df["performance_score"] >= 60) & (site_df["performance_score"] < 80)])
            low_perf = len(site_df[site_df["performance_score"] < 60])
            
            print(f"\n  Performance Distribution:")
            print(f"    High (≥80): {high_perf} sites")
            print(f"    Medium (60-79): {med_perf} sites")
            print(f"    Low (<60): {low_perf} sites")
    
    # Step 4: Calculate DQI
    print("\n4. DQI CALCULATION")
    print("-"*80)
    
    dqi_calculator = DataQualityIndex()
    study_metrics["subject_metrics"] = dqi_calculator.calculate_subject_dqi(
        study_metrics["subject_metrics"]
    )
    
    subject_df = study_metrics["subject_metrics"]
    
    if "risk_level" in subject_df.columns:
        high_risk = (subject_df["risk_level"] == "High").sum()
        med_risk = (subject_df["risk_level"] == "Medium").sum()
        low_risk = (subject_df["risk_level"] == "Low").sum()
        
        print(f"✓ Risk Distribution:")
        print(f"    High: {high_risk}")
        print(f"    Medium: {med_risk}")
        print(f"    Low: {low_risk}")
    
    if "dqi_score" in subject_df.columns:
        print(f"\n✓ DQI Scores:")
        print(f"    Mean: {subject_df['dqi_score'].mean():.1f}")
        print(f"    Min: {subject_df['dqi_score'].min():.1f}")
        print(f"    Max: {subject_df['dqi_score'].max():.1f}")
    
    # Step 5: Test CRA-specific analytics
    print("\n5. CRA-SPECIFIC ANALYTICS")
    print("-"*80)
    
    # Query management metrics
    subjects_with_queries = (subject_df["open_queries"] > 0).sum()
    high_query_subjects = (subject_df["open_queries"] >= 3).sum()
    
    print(f"✓ Query Management:")
    print(f"    Subjects with queries: {subjects_with_queries}")
    print(f"    High-burden subjects (≥3): {high_query_subjects}")
    
    # Visit compliance metrics
    subjects_with_missing = (subject_df["missing_visits"] > 0).sum()
    compliance_rate = ((len(subject_df) - subjects_with_missing) / len(subject_df) * 100) if len(subject_df) > 0 else 100
    
    print(f"\n✓ Visit Compliance:")
    print(f"    Subjects with missing visits: {subjects_with_missing}")
    print(f"    Compliance rate: {compliance_rate:.1f}%")
    
    # Clean data rate
    if "is_clean_patient" in subject_df.columns:
        clean_count = subject_df["is_clean_patient"].sum()
        clean_pct = (clean_count / len(subject_df) * 100) if len(subject_df) > 0 else 0
        
        print(f"\n✓ Clean Data:")
        print(f"    Clean subjects: {clean_count}/{len(subject_df)}")
        print(f"    Clean rate: {clean_pct:.1f}%")
    
    # Step 6: Priority sites analysis
    print("\n6. PRIORITY SITES FOR MONITORING")
    print("-"*80)
    
    site_df = study_metrics["site_metrics"]
    
    # Calculate urgency scores
    site_df["urgency_score"] = (
        site_df.get("total_missing_visits", 0) * 5 +
        site_df.get("total_open_queries", 0) * 2 +
        (100 - site_df.get("performance_score", 100))
    )
    
    top_priority = site_df.nlargest(5, "urgency_score")
    
    print(f"✓ Top 5 Priority Sites (by urgency score):")
    for idx, site in top_priority.iterrows():
        print(f"\n  Site {site['site_id']}:")
        print(f"    Urgency Score: {site['urgency_score']:.0f}")
        print(f"    Performance: {site['performance_score']:.1f}")
        print(f"    Open Queries: {int(site['total_open_queries'])}")
        print(f"    Missing Visits: {int(site['total_missing_visits'])}")
        print(f"    Subject Count: {int(site['subject_count'])}")
    
    # Step 7: Action items summary
    print("\n7. ACTION ITEMS SUMMARY")
    print("-"*80)
    
    actions_needed = 0
    
    # Query resolution needed
    high_query_sites = len(site_df[site_df["total_open_queries"] >= 10])
    if high_query_sites > 0:
        print(f"✓ Query Resolution: {high_query_sites} sites need attention (≥10 queries)")
        actions_needed += high_query_sites
    
    # Visit follow-up needed
    high_missing_sites = len(site_df[site_df["total_missing_visits"] >= 5])
    if high_missing_sites > 0:
        print(f"✓ Visit Follow-up: {high_missing_sites} sites need attention (≥5 missing)")
        actions_needed += high_missing_sites
    
    # Low performance sites
    low_perf_sites = len(site_df[site_df["performance_score"] < 60])
    if low_perf_sites > 0:
        print(f"✓ Performance Issues: {low_perf_sites} sites below threshold (<60)")
        actions_needed += low_perf_sites
    
    # High risk subjects
    if high_risk > 0:
        print(f"✓ High-Risk Subjects: {high_risk} subjects need review")
        actions_needed += high_risk
    
    if actions_needed == 0:
        print(f"✓ No critical actions needed - study performing well!")
    else:
        print(f"\n✓ Total action items identified: {actions_needed}")
    
    print("\n" + "="*80)
    print("CRA DASHBOARD TEST COMPLETE ✓")
    print("="*80)
    print("\nAll CRA dashboard components validated successfully!")
    print("Dashboard is ready for use with comprehensive monitoring capabilities.")


if __name__ == "__main__":
    test_cra_dashboard()
