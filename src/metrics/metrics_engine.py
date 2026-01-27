"""
Metrics Engine Module
Calculates all derived metrics and performance indicators
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from loguru import logger
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import CLEAN_PATIENT_CRITERIA, COLUMN_MAPPINGS


class MetricsEngine:
    """
    Core engine for calculating clinical trial metrics
    """
    
    def __init__(self, canonical_model: Dict[str, pd.DataFrame], raw_data: Dict[str, Dict[str, pd.DataFrame]]):
        """
        Initialize metrics engine
        
        Args:
            canonical_model: Dictionary of canonical entities
            raw_data: Raw ingested data
        """
        self.canonical_model = canonical_model
        self.raw_data = raw_data
        self.metrics_cache = {}
        logger.info("Metrics Engine initialized")
    
    def standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize column names using COLUMN_MAPPINGS with exact matching priority
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with standardized column names
        """
        if df is None or df.empty:
            return df
        
        logger.debug(f"standardize_column_names input: {df.shape[0]} rows x {df.shape[1]} columns")
        logger.debug(f"First 15 input columns: {list(df.columns[:15])}")
        
        df_copy = df.copy()
        renamed_cols = {}
        
        # First pass: Exact matches only
        for standard_name, variations in COLUMN_MAPPINGS.items():
            for col in df_copy.columns:
                if col in renamed_cols:
                    continue
                col_stripped = str(col).strip()
                col_lower = col_stripped.lower()
                # Exact match (case-insensitive)
                for variation in variations:
                    if col_lower == variation.lower():
                        renamed_cols[col] = standard_name
                        logger.debug(f"Metrics engine renamed '{col}' to '{standard_name}' (exact)")
                        break
        
        # Second pass: Substring matches for remaining columns
        for standard_name, variations in COLUMN_MAPPINGS.items():
            for col in df_copy.columns:
                if col in renamed_cols:
                    continue
                col_stripped = str(col).strip()
                col_lower = col_stripped.lower()
                # Check if any variation is IN the column name (not the reverse)
                for variation in variations:
                    variation_lower = variation.lower()
                    # Only match if variation is a complete substring in the column
                    if variation_lower in col_lower and len(variation_lower) > 3:  # Avoid short ambiguous matches
                        renamed_cols[col] = standard_name
                        logger.debug(f"Metrics engine renamed '{col}' to '{standard_name}' (substring)")
                        break
        
        df_copy.rename(columns=renamed_cols, inplace=True)
        return df_copy
    
    def calculate_completeness_metrics(self, edc_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate data completeness metrics from actual available columns
        
        Args:
            edc_data: EDC metrics DataFrame
            
        Returns:
            DataFrame with completeness metrics added
        """
        if edc_data is None or edc_data.empty:
            return pd.DataFrame()
        
        df = edc_data.copy()
        
        # Use actual missing_visits column if it exists (already a count)
        if "missing_visits" in df.columns:
            df["missing_visits"] = pd.to_numeric(df["missing_visits"], errors='coerce').fillna(0)
            logger.debug(f"missing_visits: min={df['missing_visits'].min()}, max={df['missing_visits'].max()}, mean={df['missing_visits'].mean():.2f}")
            # Calculate percentage if we have a baseline
            if "total_visits" in df.columns:
                df["pct_missing_visits"] = (df["missing_visits"] / df["total_visits"] * 100).fillna(0)
            else:
                # Use count directly for scoring
                max_val = df["missing_visits"].max()
                if max_val > 0:
                    df["pct_missing_visits"] = (df["missing_visits"] / max_val * 100).fillna(0)
                    logger.debug(f"pct_missing_visits (normalized): min={df['pct_missing_visits'].min()}, max={df['pct_missing_visits'].max()}, mean={df['pct_missing_visits'].mean():.2f}%")
                else:
                    df["pct_missing_visits"] = 0
                    logger.debug("All missing_visits are 0")
        else:
            logger.warning("missing_visits column NOT FOUND after standardization")
            # Legacy calculation if old format
            if all(col in df.columns for col in ["Visits Expected", "Visits Completed"]):
                df["missing_visits"] = df["Visits Expected"] - df["Visits Completed"]
                df["pct_missing_visits"] = (df["missing_visits"] / df["Visits Expected"] * 100).fillna(0)
            else:
                df["missing_visits"] = 0
                df["pct_missing_visits"] = 0
        
        # Use actual missing_pages column if it exists
        if "missing_pages" in df.columns:
            df["missing_pages"] = pd.to_numeric(df["missing_pages"], errors='coerce').fillna(0)
            logger.debug(f"missing_pages: min={df['missing_pages'].min()}, max={df['missing_pages'].max()}, mean={df['missing_pages'].mean():.2f}")
            # Calculate percentage if we have a baseline
            if "total_pages" in df.columns:
                df["pct_missing_pages"] = (df["missing_pages"] / df["total_pages"] * 100).fillna(0)
            else:
                # Use count directly for scoring
                max_val = df["missing_pages"].max()
                if max_val > 0:
                    df["pct_missing_pages"] = (df["missing_pages"] / max_val * 100).fillna(0)
                    logger.debug(f"pct_missing_pages (normalized): min={df['pct_missing_pages'].min()}, max={df['pct_missing_pages'].max()}, mean={df['pct_missing_pages'].mean():.2f}%")
                else:
                    df["pct_missing_pages"] = 0
                    logger.debug("All missing_pages are 0")
        else:
            logger.warning("missing_pages column NOT FOUND after standardization")
            # Legacy calculation
            if all(col in df.columns for col in ["Pages Expected", "Pages Completed"]):
                df["missing_pages"] = df["Pages Expected"] - df["Pages Completed"]
                df["pct_missing_pages"] = (df["missing_pages"] / df["Pages Expected"] * 100).fillna(0)
            else:
                df["missing_pages"] = 0
                df["pct_missing_pages"] = 0
        
        # Overall completeness score (100 - average missing percentage)
        df["completeness_score"] = 100 - ((df["pct_missing_visits"] + df["pct_missing_pages"]) / 2)
        df["completeness_score"] = df["completeness_score"].clip(0, 100)
        
        logger.info(f"Calculated completeness metrics for {len(df)} records")
        return df
    
    def calculate_query_metrics(self, edc_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate query-related metrics from actual available data
        
        Args:
            edc_data: EDC metrics DataFrame
            
        Returns:
            DataFrame with query metrics added
        """
        if edc_data is None or edc_data.empty:
            return pd.DataFrame()
        
        df = edc_data.copy()
        
        # Use actual open_queries column if available
        if "open_queries" in df.columns:
            df["open_queries"] = pd.to_numeric(df["open_queries"], errors='coerce').fillna(0)
        elif "Open Queries" in df.columns:
            df["open_queries"] = pd.to_numeric(df["Open Queries"], errors='coerce').fillna(0)
        else:
            df["open_queries"] = 0
        
        # Use actual closed_queries column if available
        if "closed_queries" in df.columns:
            df["closed_queries"] = pd.to_numeric(df["closed_queries"], errors='coerce').fillna(0)
        elif "Closed Queries" in df.columns:
            df["closed_queries"] = pd.to_numeric(df["Closed Queries"], errors='coerce').fillna(0)
        else:
            df["closed_queries"] = 0
        
        # Total queries
        df["total_queries"] = df["open_queries"] + df["closed_queries"]
        
        # Query resolution rate
        df["query_resolution_rate"] = np.where(
            df["total_queries"] > 0,
            (df["closed_queries"] / df["total_queries"] * 100),
            100
        )
        
        # Query burden indicator - more than 5 open queries is high burden
        df["high_query_burden"] = df["open_queries"] > 5
        
        logger.info(f"Calculated query metrics for {len(df)} records")
        return df
    
    def calculate_sdv_metrics(self, edc_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Source Data Verification metrics
        
        Args:
            edc_data: EDC metrics DataFrame
            
        Returns:
            DataFrame with SDV metrics added
        """
        if edc_data is None or edc_data.empty:
            return pd.DataFrame()
        
        df = edc_data.copy()
        
        # SDV completion
        if "SDV Status" in df.columns:
            df["sdv_complete"] = df["SDV Status"].isin(["Complete", "Completed", "100%"])
            df["pct_sdv_complete"] = df.groupby("Site ID")["sdv_complete"].transform("mean") * 100 if "Site ID" in df.columns else 0
        else:
            df["sdv_complete"] = False
            df["pct_sdv_complete"] = 0
        
        logger.info(f"Calculated SDV metrics for {len(df)} records")
        return df
    
    def calculate_safety_metrics(self, study_name: str) -> Dict:
        """
        Calculate safety-related metrics for a study
        
        Args:
            study_name: Name of the study
            
        Returns:
            Dictionary of safety metrics
        """
        metrics = {
            "total_saes": 0,
            "open_saes": 0,
            "closed_saes": 0,
            "overdue_follow_ups": 0,
            "serious_events_rate": 0
        }
        
        if study_name not in self.raw_data:
            return metrics
        
        study_df = self.raw_data[study_name]
        
        if study_df is not None and not study_df.empty and "sae_review" in study_df.columns:
            metrics["total_saes"] = int(study_df["sae_review"].sum())
            
            # All SAEs in our data are issues to review
            metrics["open_saes"] = metrics["total_saes"]
            metrics["closed_saes"] = 0
            
            logger.info(f"Calculated safety metrics for {study_name}: {metrics['total_saes']} total SAEs")
        
        return metrics
    
    def calculate_site_performance_metrics(self, study_name: str) -> pd.DataFrame:
        """
        Calculate site-level performance metrics
        
        Args:
            study_name: Name of the study
            
        Returns:
            DataFrame with site performance metrics
        """
        if study_name not in self.raw_data:
            return pd.DataFrame()
        
        study_df = self.raw_data[study_name]
        
        if study_df is None or study_df.empty:
            return pd.DataFrame()
        
        edc_df = study_df
        
        if "site_id" not in edc_df.columns:
            return pd.DataFrame()
        
        # Aggregate by site
        agg_dict = {
            "subject_id": "count",
            "missing_visits": "sum",
            "missing_pages": "sum",
            "open_queries": "sum"
        }
        
        site_metrics = edc_df.groupby("site_id").agg(agg_dict).reset_index()
        site_metrics.columns = ["site_id", "subject_count", "total_missing_visits", 
                                "total_missing_pages", "total_open_queries"]
        
        site_metrics["study_id"] = study_name
        
        # Performance score (simple weighted average)
        site_metrics["performance_score"] = (
            100 - 
            (site_metrics["total_missing_visits"] * 2 + 
             site_metrics["total_missing_pages"] * 1 + 
             site_metrics["total_open_queries"] * 3) / 
            site_metrics["subject_count"]
        ).clip(0, 100)
        
        logger.info(f"Calculated site performance metrics for {len(site_metrics)} sites in {study_name}")
        return site_metrics
    
    def assess_clean_patient_status(self, subject_row: pd.Series) -> bool:
        """
        Assess if a patient meets clean patient criteria
        
        Clean patient rule (exact specification):
        - missing_visits == 0
        - missing_pages == 0
        - open_queries == 0
        - pending_sdv == 0
        - open_safety_issues == 0
        
        Args:
            subject_row: Series representing a single subject
            
        Returns:
            True if patient is clean, False otherwise
        """
        is_clean = True
        
        # Check the 5 required criteria only
        required_criteria = {
            "missing_visits": 0,
            "missing_pages": 0,
            "open_queries": 0,
            "pending_sdv": 0,
            "open_safety_issues": 0
        }
        
        for col, threshold in required_criteria.items():
            if col in subject_row.index:
                value = pd.to_numeric(subject_row[col], errors='coerce')
                if pd.isna(value):
                    value = 0
                if value > threshold:
                    is_clean = False
                    break
        
        return is_clean
    
    def calculate_clean_patients(self, edc_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate clean patient status for all subjects
        
        Args:
            edc_data: EDC metrics DataFrame with all metrics calculated
            
        Returns:
            DataFrame with clean status added
        """
        if edc_data is None or edc_data.empty:
            return pd.DataFrame()
        
        df = edc_data.copy()
        
        # Check if is_clean_patient already calculated by multi_file_loader
        if "is_clean_patient" in df.columns:
            logger.info(f"Clean patient flag already exists from loader - using existing values")
            clean_count = df["is_clean_patient"].sum()
            total_count = len(df)
            pct_clean = (clean_count / total_count * 100) if total_count > 0 else 0
            logger.info(f"Clean patients: {clean_count}/{total_count} ({pct_clean:.1f}%)")
            return df
        
        # Ensure all required columns exist
        required_cols = list(CLEAN_PATIENT_CRITERIA.keys())
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0
        
        # Apply clean patient logic
        df["is_clean_patient"] = df.apply(self.assess_clean_patient_status, axis=1)
        
        clean_count = df["is_clean_patient"].sum()
        total_count = len(df)
        pct_clean = (clean_count / total_count * 100) if total_count > 0 else 0
        
        logger.info(f"Clean patients: {clean_count}/{total_count} ({pct_clean:.1f}%)")
        
        return df
    
    def calculate_all_metrics_for_study(self, study_name: str) -> Dict[str, pd.DataFrame]:
        """
        Calculate all metrics for a specific study
        
        Args:
            study_name: Name of the study
            
        Returns:
            Dictionary containing all calculated metrics
        """
        logger.info(f"Calculating all metrics for {study_name}")
        
        results = {}
        
        if study_name not in self.raw_data:
            logger.warning(f"Study {study_name} not found in raw data")
            return results
        
        study_df = self.raw_data[study_name]
        
        # Data is already consolidated with metrics columns, just need to calculate percentages
        if study_df is not None and not study_df.empty:
            # Calculate completeness metrics (percentages from counts)
            study_df = self.calculate_completeness_metrics(study_df)
            
            # Calculate query metrics (percentages from counts)
            study_df = self.calculate_query_metrics(study_df)
            
            # Calculate SDV metrics if SDV columns exist
            study_df = self.calculate_sdv_metrics(study_df)
            
            # Calculate clean patient status
            study_df = self.calculate_clean_patients(study_df)
            
            results["subject_metrics"] = study_df
        
        # Calculate site-level metrics
        site_metrics = self.calculate_site_performance_metrics(study_name)
        if not site_metrics.empty:
            results["site_metrics"] = site_metrics
        
        # Calculate safety metrics
        safety_metrics = self.calculate_safety_metrics(study_name)
        results["safety_metrics"] = safety_metrics
        
        # Cache results
        self.metrics_cache[study_name] = results
        
        return results
    
    def get_study_summary(self, study_name: str) -> Dict:
        """
        Get high-level summary metrics for a study
        
        Args:
            study_name: Name of the study
            
        Returns:
            Dictionary of summary statistics
        """
        if study_name not in self.metrics_cache:
            self.calculate_all_metrics_for_study(study_name)
        
        metrics = self.metrics_cache.get(study_name, {})
        
        summary = {
            "study_id": study_name,
            "total_subjects": 0,
            "clean_subjects": 0,
            "pct_clean": 0,
            "avg_completeness": 0,
            "total_open_queries": 0,
            "total_saes": 0
        }
        
        if "subject_metrics" in metrics:
            subject_df = metrics["subject_metrics"]
            summary["total_subjects"] = len(subject_df)
            
            if "is_clean_patient" in subject_df.columns:
                summary["clean_subjects"] = subject_df["is_clean_patient"].sum()
                summary["pct_clean"] = (summary["clean_subjects"] / summary["total_subjects"] * 100) if summary["total_subjects"] > 0 else 0
            
            if "completeness_score" in subject_df.columns:
                summary["avg_completeness"] = subject_df["completeness_score"].mean()
            
            if "open_queries" in subject_df.columns:
                summary["total_open_queries"] = subject_df["open_queries"].sum()
        
        if "safety_metrics" in metrics:
            summary["total_saes"] = metrics["safety_metrics"]["total_saes"]
            summary["open_saes"] = metrics["safety_metrics"]["open_saes"]
        
        return summary
