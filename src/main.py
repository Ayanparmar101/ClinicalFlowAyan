"""
Main application entry point for CLI and batch processing
"""
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/ctip_{time}.log",
    rotation="500 MB",
    retention="10 days",
    level="DEBUG"
)

from ingestion import DataIngestionEngine
from harmonization import CanonicalDataModel
from metrics import MetricsEngine, DataQualityIndex
from intelligence import RiskIntelligence
from ai import GenerativeAI, CRAAgent, DataQualityAgent, TrialManagerAgent
from config import DATA_PATH, OUTPUT_PATH


def main():
    """
    Main execution function
    """
    logger.info("=" * 80)
    logger.info("Clinical Trial Intelligence Platform - Starting Processing")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    try:
        # Step 1: Data Ingestion
        logger.info("Step 1/6: Data Ingestion")
        ingestion_engine = DataIngestionEngine(DATA_PATH)
        all_data = ingestion_engine.ingest_all_studies()
        
        if not all_data:
            logger.error("No data found. Please place data files in the /data directory.")
            return
        
        logger.info(f"Successfully ingested {len(all_data)} studies")
        
        # Step 2: Harmonization
        logger.info("Step 2/6: Data Harmonization")
        canonical_model = CanonicalDataModel()
        canonical_entities = canonical_model.build_canonical_model(all_data)
        
        logger.info(f"Built canonical model with {len(canonical_entities)} entity types")
        
        # Step 3: Metrics Calculation
        logger.info("Step 3/6: Metrics Calculation")
        metrics_engine = MetricsEngine(canonical_entities, all_data)
        all_metrics = {}
        
        for study_name in all_data.keys():
            logger.info(f"Calculating metrics for {study_name}")
            study_metrics = metrics_engine.calculate_all_metrics_for_study(study_name)
            all_metrics[study_name] = study_metrics
        
        # Step 4: Data Quality Index
        logger.info("Step 4/6: Data Quality Index Calculation")
        dqi_calculator = DataQualityIndex()
        
        for study_name, metrics in all_metrics.items():
            if "subject_metrics" in metrics:
                logger.info(f"Calculating DQI for {study_name}")
                metrics["subject_metrics"] = dqi_calculator.calculate_subject_dqi(
                    metrics["subject_metrics"]
                )
                
                # Calculate study-level DQI
                study_dqi = dqi_calculator.calculate_study_dqi(metrics["subject_metrics"])
                logger.info(f"Study {study_name} DQI: {study_dqi.get('overall_dqi', 0):.2f}")
        
        # Step 5: Risk Intelligence
        logger.info("Step 5/6: Risk Intelligence Analysis")
        risk_engine = RiskIntelligence(all_metrics)
        
        for study_name in all_metrics.keys():
            logger.info(f"Generating risk report for {study_name}")
            risk_report = risk_engine.generate_risk_report(study_name)
            
            critical_count = risk_report["risk_summary"]["critical_issues_count"]
            logger.info(f"Study {study_name}: {critical_count} critical issues detected")
        
        # Step 6: AI Insights (optional)
        logger.info("Step 6/6: AI Insights Generation")
        gen_ai = GenerativeAI()
        
        # Generate portfolio summary
        logger.info("Generating portfolio insights...")
        
        # Export results
        logger.info("Exporting results...")
        export_results(all_metrics, OUTPUT_PATH)
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info(f"Processing Complete!")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Studies Processed: {len(all_data)}")
        logger.info(f"Results saved to: {OUTPUT_PATH}")
        logger.info("=" * 80)
        
        print(f"\n✅ Success! Processing complete in {duration:.2f} seconds")
        print(f"📊 Results saved to: {OUTPUT_PATH}")
        print(f"\nTo view the interactive dashboard, run:")
        print(f"  streamlit run src/dashboard/app.py")
        
    except Exception as e:
        logger.exception(f"Error during processing: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def export_results(all_metrics: dict, output_path: Path):
    """
    Export processing results to files
    
    Args:
        all_metrics: Dictionary of all calculated metrics
        output_path: Path to output directory
    """
    output_path.mkdir(exist_ok=True)
    
    for study_name, metrics in all_metrics.items():
        study_output_dir = output_path / study_name
        study_output_dir.mkdir(exist_ok=True)
        
        # Export subject metrics
        if "subject_metrics" in metrics:
            subject_df = metrics["subject_metrics"]
            output_file = study_output_dir / f"{study_name}_subject_metrics.csv"
            subject_df.to_csv(output_file, index=False)
            logger.info(f"Exported subject metrics to {output_file}")
        
        # Export site metrics
        if "site_metrics" in metrics:
            site_df = metrics["site_metrics"]
            output_file = study_output_dir / f"{study_name}_site_metrics.csv"
            site_df.to_csv(output_file, index=False)
            logger.info(f"Exported site metrics to {output_file}")
    
    logger.info(f"All results exported to {output_path}")


if __name__ == "__main__":
    main()
