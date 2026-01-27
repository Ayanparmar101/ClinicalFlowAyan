"""
Risk Intelligence Module
Proactive detection of operational bottlenecks and data quality issues
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from loguru import logger


class RiskIntelligence:
    """
    Detects patterns, trends, and risks in clinical trial operations
    """
    
    def __init__(self, metrics_data: Dict):
        """
        Initialize risk intelligence engine
        
        Args:
            metrics_data: Dictionary containing calculated metrics
        """
        self.metrics_data = metrics_data
        self.risk_signals = []
        logger.info("Risk Intelligence Engine initialized")
    
    def detect_high_risk_sites(self, site_metrics: pd.DataFrame, threshold: float = 70) -> List[Dict]:
        """
        Identify sites with high operational risk
        
        Args:
            site_metrics: DataFrame containing site-level metrics
            threshold: Risk score threshold
            
        Returns:
            List of high-risk site records
        """
        if site_metrics is None or site_metrics.empty:
            return []
        
        high_risk = []
        
        if "performance_score" in site_metrics.columns:
            risky_sites = site_metrics[site_metrics["performance_score"] < threshold]
            
            for _, site in risky_sites.iterrows():
                risk_record = {
                    "entity_type": "site",
                    "entity_id": site.get("site_id", "Unknown"),
                    "study_id": site.get("study_id", "Unknown"),
                    "risk_level": "High",
                    "risk_score": site.get("performance_score", 0),
                    "risk_factors": self._identify_site_risk_factors(site),
                    "detected_at": datetime.now()
                }
                high_risk.append(risk_record)
        
        logger.info(f"Detected {len(high_risk)} high-risk sites")
        return high_risk
    
    def _identify_site_risk_factors(self, site_row: pd.Series) -> List[str]:
        """
        Identify specific risk factors for a site
        
        Args:
            site_row: Series containing site metrics
            
        Returns:
            List of risk factor descriptions
        """
        factors = []
        
        if "total_missing_visits" in site_row.index and site_row["total_missing_visits"] > 10:
            factors.append(f"High missing visits: {site_row['total_missing_visits']}")
        
        if "total_open_queries" in site_row.index and site_row["total_open_queries"] > 20:
            factors.append(f"High query burden: {site_row['total_open_queries']} open queries")
        
        if "total_missing_pages" in site_row.index and site_row["total_missing_pages"] > 15:
            factors.append(f"Significant data gaps: {site_row['total_missing_pages']} missing pages")
        
        return factors if factors else ["Multiple operational issues"]
    
    def detect_high_risk_subjects(self, subject_metrics: pd.DataFrame) -> List[Dict]:
        """
        Identify subjects with critical data quality issues
        
        Args:
            subject_metrics: DataFrame containing subject-level metrics with DQI
            
        Returns:
            List of high-risk subject records
        """
        if subject_metrics is None or subject_metrics.empty:
            return []
        
        high_risk = []
        
        if "risk_level" in subject_metrics.columns:
            risky_subjects = subject_metrics[subject_metrics["risk_level"] == "High"]
            
            for _, subject in risky_subjects.iterrows():
                risk_record = {
                    "entity_type": "subject",
                    "entity_id": subject.get("Subject ID", "Unknown"),
                    "site_id": subject.get("Site ID", "Unknown"),
                    "study_id": subject.get("_study", "Unknown"),
                    "risk_level": "High",
                    "dqi_score": subject.get("dqi_score", 0),
                    "risk_factors": self._identify_subject_risk_factors(subject),
                    "detected_at": datetime.now()
                }
                high_risk.append(risk_record)
        
        logger.info(f"Detected {len(high_risk)} high-risk subjects")
        return high_risk
    
    def _identify_subject_risk_factors(self, subject_row: pd.Series) -> List[str]:
        """
        Identify specific risk factors for a subject
        
        Args:
            subject_row: Series containing subject metrics
            
        Returns:
            List of risk factor descriptions
        """
        factors = []
        
        if "open_queries" in subject_row.index and subject_row["open_queries"] > 3:
            factors.append(f"{subject_row['open_queries']} unresolved queries")
        
        if "missing_visits" in subject_row.index and subject_row["missing_visits"] > 0:
            factors.append(f"{subject_row['missing_visits']} missing visits")
        
        if "missing_pages" in subject_row.index and subject_row["missing_pages"] > 5:
            factors.append(f"{subject_row['missing_pages']} missing pages")
        
        if "sdv_complete" in subject_row.index and not subject_row["sdv_complete"]:
            factors.append("SDV incomplete")
        
        if "open_safety_issues" in subject_row.index and subject_row["open_safety_issues"] > 0:
            factors.append(f"{subject_row['open_safety_issues']} open safety issues")
        
        return factors if factors else ["Data quality concerns"]
    
    def detect_query_hotspots(self, subject_metrics: pd.DataFrame, threshold: int = 5) -> List[Dict]:
        """
        Identify locations with high query concentrations
        
        Args:
            subject_metrics: DataFrame containing subject metrics
            threshold: Query count threshold per subject
            
        Returns:
            List of query hotspot records
        """
        if subject_metrics is None or subject_metrics.empty:
            return []
        
        hotspots = []
        
        if all(col in subject_metrics.columns for col in ["Site ID", "open_queries"]):
            # Group by site and count high-query subjects
            site_query_issues = subject_metrics[subject_metrics["open_queries"] >= threshold]
            
            if not site_query_issues.empty:
                hotspot_summary = site_query_issues.groupby("Site ID").agg({
                    "Subject ID": "count",
                    "open_queries": "sum"
                }).reset_index()
                
                for _, row in hotspot_summary.iterrows():
                    hotspot = {
                        "entity_type": "query_hotspot",
                        "entity_id": row["Site ID"],
                        "affected_subjects": row["Subject ID"],
                        "total_open_queries": row["open_queries"],
                        "severity": "High" if row["open_queries"] > 50 else "Medium",
                        "detected_at": datetime.now()
                    }
                    hotspots.append(hotspot)
        
        logger.info(f"Detected {len(hotspots)} query hotspots")
        return hotspots
    
    def assess_interim_analysis_readiness(self, study_metrics: Dict) -> Dict:
        """
        Assess if study data is ready for interim analysis
        
        Args:
            study_metrics: Dictionary containing study-level metrics
            
        Returns:
            Readiness assessment dictionary
        """
        assessment = {
            "ready": False,
            "overall_score": 0,
            "blocking_issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Criterion 1: Clean patient percentage
        if "pct_clean" in study_metrics:
            pct_clean = study_metrics["pct_clean"]
            if pct_clean >= 90:
                assessment["overall_score"] += 40
            elif pct_clean >= 75:
                assessment["overall_score"] += 30
                assessment["warnings"].append(f"Only {pct_clean:.1f}% clean patients (target: 90%)")
            else:
                assessment["blocking_issues"].append(f"Insufficient clean patients: {pct_clean:.1f}% (minimum: 75%)")
        
        # Criterion 2: Open queries
        if "total_open_queries" in study_metrics:
            open_queries = study_metrics["total_open_queries"]
            total_subjects = study_metrics.get("total_subjects", 1)
            queries_per_subject = open_queries / total_subjects
            
            if queries_per_subject <= 1:
                assessment["overall_score"] += 30
            elif queries_per_subject <= 2:
                assessment["overall_score"] += 20
                assessment["warnings"].append(f"Moderate query burden: {queries_per_subject:.1f} queries/subject")
            else:
                assessment["blocking_issues"].append(f"High query burden: {queries_per_subject:.1f} queries/subject")
        
        # Criterion 3: Safety events
        if "open_saes" in study_metrics:
            open_saes = study_metrics["open_saes"]
            if open_saes == 0:
                assessment["overall_score"] += 30
            elif open_saes <= 3:
                assessment["overall_score"] += 20
                assessment["warnings"].append(f"{open_saes} unresolved safety events")
            else:
                assessment["blocking_issues"].append(f"{open_saes} unresolved safety events must be addressed")
        
        # Determine readiness
        assessment["ready"] = assessment["overall_score"] >= 70 and len(assessment["blocking_issues"]) == 0
        
        # Generate recommendations
        if not assessment["ready"]:
            if assessment["blocking_issues"]:
                assessment["recommendations"].append("Address all blocking issues before proceeding")
            if assessment["warnings"]:
                assessment["recommendations"].append("Resolve warning items to improve data quality")
        
        logger.info(f"Interim analysis readiness: {'READY' if assessment['ready'] else 'NOT READY'} " +
                   f"(score: {assessment['overall_score']}/100)")
        
        return assessment
    
    def detect_site_trends(self, historical_metrics: List[pd.DataFrame]) -> List[Dict]:
        """
        Detect worsening or improving trends at site level
        
        Args:
            historical_metrics: List of site metrics DataFrames over time
            
        Returns:
            List of trend records
        """
        trends = []
        
        if not historical_metrics or len(historical_metrics) < 2:
            logger.warning("Insufficient historical data for trend analysis")
            return trends
        
        # Compare most recent vs previous
        current = historical_metrics[-1]
        previous = historical_metrics[-2]
        
        if all(df is not None and not df.empty for df in [current, previous]):
            if all("site_id" in df.columns and "performance_score" in df.columns for df in [current, previous]):
                # Merge on site_id
                merged = current[["site_id", "performance_score"]].merge(
                    previous[["site_id", "performance_score"]],
                    on="site_id",
                    suffixes=("_current", "_previous")
                )
                
                merged["score_change"] = merged["performance_score_current"] - merged["performance_score_previous"]
                
                # Identify significant changes
                worsening = merged[merged["score_change"] < -10]
                improving = merged[merged["score_change"] > 10]
                
                for _, site in worsening.iterrows():
                    trends.append({
                        "site_id": site["site_id"],
                        "trend": "worsening",
                        "score_change": site["score_change"],
                        "severity": "High" if site["score_change"] < -20 else "Medium"
                    })
                
                for _, site in improving.iterrows():
                    trends.append({
                        "site_id": site["site_id"],
                        "trend": "improving",
                        "score_change": site["score_change"],
                        "severity": "Positive"
                    })
        
        logger.info(f"Detected {len(trends)} site trends")
        return trends
    
    def generate_risk_report(self, study_name: str) -> Dict:
        """
        Generate comprehensive risk report for a study
        
        Args:
            study_name: Name of the study
            
        Returns:
            Comprehensive risk report dictionary
        """
        report = {
            "study_id": study_name,
            "generated_at": datetime.now(),
            "risk_summary": {
                "high_risk_sites": [],
                "high_risk_subjects": [],
                "query_hotspots": [],
                "critical_issues_count": 0
            },
            "readiness_assessment": {},
            "recommended_actions": []
        }
        
        # Get metrics for study
        if study_name in self.metrics_data:
            study_metrics = self.metrics_data[study_name]
            
            # Detect high-risk sites
            if "site_metrics" in study_metrics:
                report["risk_summary"]["high_risk_sites"] = self.detect_high_risk_sites(
                    study_metrics["site_metrics"]
                )
            
            # Detect high-risk subjects
            if "subject_metrics" in study_metrics:
                report["risk_summary"]["high_risk_subjects"] = self.detect_high_risk_subjects(
                    study_metrics["subject_metrics"]
                )
                report["risk_summary"]["query_hotspots"] = self.detect_query_hotspots(
                    study_metrics["subject_metrics"]
                )
            
            # Count critical issues
            report["risk_summary"]["critical_issues_count"] = (
                len(report["risk_summary"]["high_risk_sites"]) +
                len(report["risk_summary"]["high_risk_subjects"]) +
                len(report["risk_summary"]["query_hotspots"])
            )
        
        logger.info(f"Generated risk report for {study_name}: " +
                   f"{report['risk_summary']['critical_issues_count']} critical issues")
        
        return report
