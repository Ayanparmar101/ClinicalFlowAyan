"""
Quick fix for metrics engine to work with consolidated DataFrames
"""
import sys
from pathlib import Path

# Read the file
metrics_file = Path("src/metrics/metrics_engine.py")
content = metrics_file.read_text()

# Fix 1: Update calculate_safety_metrics
content = content.replace(
    '''        if study_name not in self.raw_data:
            return metrics
        
        study_data = self.raw_data[study_name]
        
        if "sae_dashboard" in study_data:
            sae_df = study_data["sae_dashboard"]
            
            metrics["total_saes"] = len(sae_df)''',
    '''        if study_name not in self.raw_data:
            return metrics
        
        study_df = self.raw_data[study_name]
        
        if study_df is not None and not study_df.empty and "sae_review" in study_df.columns:
            metrics["total_saes"] = int(study_df["sae_review"].sum())
            sae_count = metrics["total_saes"]'''
)

# Fix 2: Update site_performance column references
content = content.replace('study_data = self.raw_data[study_name]\n        \n        if "edc_metrics" not in study_data:\n            return pd.DataFrame()\n        \n        edc_df = study_data["edc_metrics"]',
                            'study_df = self.raw_data[study_name]\n        \n        if study_df is None or study_df.empty:\n            return pd.DataFrame()\n        \n        edc_df = study_df')

content = content.replace('"Site ID"', '"site_id"')
content = content.replace('"Subject ID"', '"subject_id"')
content = content.replace('.groupby("Site ID")', '.groupby("site_id")')

# Write back
metrics_file.write_text(content)
print("✓ Fixed metrics_engine.py")
