"""
Data Quality Index (DQI) Calculator
Composite scoring system for data quality assessment
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
from loguru import logger
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import DQI_WEIGHTS, RISK_THRESHOLDS


class DataQualityIndex:
    """
    Calculates and manages Data Quality Index scoring
    """
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize DQI calculator
        
        Args:
            weights: Custom weights for DQI components (uses config defaults if None)
        """
        self.weights = weights or DQI_WEIGHTS
        self._validate_weights()
        logger.info(f"Data Quality Index initialized with weights: {self.weights}")
    
    def _validate_weights(self):
        """Validate that weights sum to 1.0"""
        total_weight = sum(self.weights.values())
        if not np.isclose(total_weight, 1.0, atol=0.01):
            logger.warning(f"Weights sum to {total_weight}, not 1.0. Normalizing...")
            # Normalize weights
            for key in self.weights:
                self.weights[key] = self.weights[key] / total_weight
    
    def calculate_component_scores(self, subject_row: pd.Series) -> Dict[str, float]:
        """
        Calculate individual component scores for DQI
        Only includes components where actual data exists - no assumptions
        
        Args:
            subject_row: Series representing a single subject's metrics
            
        Returns:
            Dictionary of component scores (0-100 scale)
        """
        scores = {}
        
        # Safety issues score (inverse - more issues = lower score)
        if "open_safety_issues" in subject_row.index and pd.notna(subject_row["open_safety_issues"]):
            scores["safety_issues"] = max(0, 100 - (subject_row["open_safety_issues"] * 20))
        
        # Missing visits score
        if "pct_missing_visits" in subject_row.index and pd.notna(subject_row["pct_missing_visits"]):
            scores["missing_visits"] = max(0, 100 - subject_row["pct_missing_visits"])
        elif "missing_visits" in subject_row.index and pd.notna(subject_row["missing_visits"]):
            # Use raw count if percentage not available
            penalty = min(100, subject_row["missing_visits"] * 5)  # 5 points per missing visit
            scores["missing_visits"] = max(0, 100 - penalty)
        
        # Open queries score
        if "open_queries" in subject_row.index and pd.notna(subject_row["open_queries"]):
            # Penalize based on query count (5+ queries = significant impact)
            penalty = min(100, subject_row["open_queries"] * 10)
            scores["open_queries"] = max(0, 100 - penalty)
        
        # Missing pages score
        if "pct_missing_pages" in subject_row.index and pd.notna(subject_row["pct_missing_pages"]):
            scores["missing_pages"] = max(0, 100 - subject_row["pct_missing_pages"])
        elif "missing_pages" in subject_row.index and pd.notna(subject_row["missing_pages"]):
            # Use raw count if percentage not available
            penalty = min(100, subject_row["missing_pages"] * 2)  # 2 points per missing page
            scores["missing_pages"] = max(0, 100 - penalty)
        
        # Coding delays - skip if no data
        
        # SDV incomplete score
        if "sdv_complete" in subject_row.index and pd.notna(subject_row["sdv_complete"]):
            scores["sdv_incomplete"] = 100 if subject_row["sdv_complete"] else 50
        
        # Completeness score - use if available
        if "completeness_score" in subject_row.index and pd.notna(subject_row["completeness_score"]):
            scores["completeness"] = subject_row["completeness_score"]
        
        # Query resolution rate - use if available
        if "query_resolution_rate" in subject_row.index and pd.notna(subject_row["query_resolution_rate"]):
            scores["query_resolution"] = subject_row["query_resolution_rate"]
        
        return scores
    
    def calculate_dqi_score(self, component_scores: Dict[str, float]) -> float:
        """
        Calculate overall DQI score from components
        Uses dynamic weighting based on available components
        
        Args:
            component_scores: Dictionary of component scores
            
        Returns:
            Overall DQI score (0-100), or None if no valid components
        """
        if not component_scores:
            # No data available to calculate DQI
            return None
        
        # Calculate weighted average using only available components
        total_score = 0.0
        total_weight = 0.0
        
        for component, score in component_scores.items():
            # Use weight if defined, otherwise equal weighting
            weight = self.weights.get(component, 1.0 / len(component_scores))
            total_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return None
        
        # Normalize by actual weights used
        dqi = total_score / total_weight if total_weight > 0 else 0
        
        return round(dqi, 2)
    
    def classify_risk_level(self, dqi_score: float) -> str:
        """
        Classify risk level based on DQI score
        
        Args:
            dqi_score: DQI score (0-100)
            
        Returns:
            Risk level: "Low", "Medium", or "High"
        """
        if dqi_score >= RISK_THRESHOLDS["medium"]:
            return "Low"
        elif dqi_score >= RISK_THRESHOLDS["high"]:
            return "Medium"
        else:
            return "High"
    
    def calculate_subject_dqi(self, subject_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate DQI for all subjects in a DataFrame
        
        Args:
            subject_data: DataFrame containing subject metrics
            
        Returns:
            DataFrame with DQI scores and risk levels added
        """
        if subject_data is None or subject_data.empty:
            return pd.DataFrame()
        
        df = subject_data.copy()
        
        # Calculate component scores for each subject
        component_scores_list = []
        dqi_scores = []
        risk_levels = []
        
        for idx, row in df.iterrows():
            components = self.calculate_component_scores(row)
            dqi = self.calculate_dqi_score(components)
            risk = self.classify_risk_level(dqi) if dqi is not None else "Unknown"
            
            component_scores_list.append(components)
            dqi_scores.append(dqi if dqi is not None else np.nan)
            risk_levels.append(risk)
        
        df["dqi_score"] = dqi_scores
        df["risk_level"] = risk_levels
        
        # Add component scores as separate columns for transparency
        for component in self.weights.keys():
            df[f"dqi_component_{component}"] = [cs.get(component, 0) for cs in component_scores_list]
        
        logger.info(f"Calculated DQI for {len(df)} subjects. Risk distribution: " +
                   f"High={sum(1 for r in risk_levels if r == 'High')}, " +
                   f"Medium={sum(1 for r in risk_levels if r == 'Medium')}, " +
                   f"Low={sum(1 for r in risk_levels if r == 'Low')}")
        
        return df
    
    def calculate_site_dqi(self, subject_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate aggregated DQI for sites
        
        Args:
            subject_data: DataFrame containing subject metrics with DQI scores
            
        Returns:
            DataFrame with site-level DQI
        """
        if subject_data is None or subject_data.empty or "Site ID" not in subject_data.columns:
            return pd.DataFrame()
        
        site_dqi = subject_data.groupby("Site ID").agg({
            "dqi_score": "mean",
            "Subject ID": "count",
            "risk_level": lambda x: x.value_counts().index[0] if len(x) > 0 else "Unknown"  # Most common risk level
        }).reset_index()
        
        site_dqi.columns = ["site_id", "avg_dqi_score", "subject_count", "primary_risk_level"]
        
        # Count subjects by risk level per site
        risk_counts = subject_data.groupby(["Site ID", "risk_level"]).size().unstack(fill_value=0)
        site_dqi = site_dqi.merge(risk_counts, left_on="site_id", right_index=True, how="left")
        
        logger.info(f"Calculated DQI for {len(site_dqi)} sites")
        return site_dqi
    
    def calculate_study_dqi(self, subject_data: pd.DataFrame) -> Dict:
        """
        Calculate overall study-level DQI
        
        Args:
            subject_data: DataFrame containing subject metrics with DQI scores
            
        Returns:
            Dictionary with study-level DQI metrics
        """
        if subject_data is None or subject_data.empty:
            return {
                "overall_dqi": None,
                "median_dqi": None,
                "min_dqi": None,
                "max_dqi": None,
                "std_dqi": None,
                "subjects_high_risk": 0,
                "subjects_medium_risk": 0,
                "subjects_low_risk": 0,
                "pct_high_risk": 0,
                "data_availability": "No data"
            }
        
        # Filter out None/NaN DQI scores
        valid_dqi = subject_data["dqi_score"].dropna()
        
        if len(valid_dqi) == 0:
            return {
                "overall_dqi": None,
                "median_dqi": None,
                "min_dqi": None,
                "max_dqi": None,
                "std_dqi": None,
                "subjects_high_risk": 0,
                "subjects_medium_risk": 0,
                "subjects_low_risk": 0,
                "pct_high_risk": 0,
                "data_availability": "Insufficient data for DQI calculation"
            }
        
        study_dqi = {
            "overall_dqi": valid_dqi.mean(),
            "median_dqi": valid_dqi.median(),
            "min_dqi": valid_dqi.min(),
            "max_dqi": valid_dqi.max(),
            "std_dqi": valid_dqi.std(),
            "subjects_high_risk": (subject_data["risk_level"] == "High").sum(),
            "subjects_medium_risk": (subject_data["risk_level"] == "Medium").sum(),
            "subjects_low_risk": (subject_data["risk_level"] == "Low").sum(),
            "pct_high_risk": (subject_data["risk_level"] == "High").sum() / len(subject_data) * 100,
            "data_availability": f"{len(valid_dqi)}/{len(subject_data)} subjects with DQI"
        }
        
        logger.info(f"Study DQI: {study_dqi['overall_dqi']:.2f if study_dqi['overall_dqi'] else 'N/A'} " +
                   f"({study_dqi['subjects_high_risk']} high-risk subjects, {study_dqi['data_availability']})")
        
        return study_dqi
    
    def identify_critical_issues(self, subject_data: pd.DataFrame, threshold: float = 70) -> pd.DataFrame:
        """
        Identify subjects/sites with critical data quality issues
        
        Args:
            subject_data: DataFrame with DQI scores
            threshold: DQI score threshold for critical issues
            
        Returns:
            DataFrame of subjects below threshold with issue details
        """
        if subject_data is None or subject_data.empty or "dqi_score" not in subject_data.columns:
            return pd.DataFrame()
        
        critical = subject_data[subject_data["dqi_score"] < threshold].copy()
        
        # Identify primary issue for each critical subject
        component_cols = [col for col in critical.columns if col.startswith("dqi_component_")]
        
        if component_cols:
            critical["primary_issue"] = critical[component_cols].idxmin(axis=1).str.replace("dqi_component_", "")
        
        logger.info(f"Identified {len(critical)} subjects with critical DQI issues (threshold: {threshold})")
        
        return critical
