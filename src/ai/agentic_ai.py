"""
Agentic AI Module
Role-based intelligent agents that provide proactive recommendations
"""
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

from .generative_ai import GenerativeAI


class AgenticAI:
    """
    Base class for intelligent agents
    """
    
    def __init__(self, agent_name: str, role: str, generative_ai: Optional[GenerativeAI] = None):
        """
        Initialize agent
        
        Args:
            agent_name: Name/ID of the agent
            role: Role description
            generative_ai: GenerativeAI instance for enhanced capabilities
        """
        self.agent_name = agent_name
        self.role = role
        self.generative_ai = generative_ai or GenerativeAI()
        self.recommendations = []
        logger.info(f"Agent '{agent_name}' ({role}) initialized")
    
    def log_recommendation(self, recommendation: Dict):
        """Log a recommendation made by the agent"""
        recommendation["agent"] = self.agent_name
        recommendation["timestamp"] = datetime.now()
        self.recommendations.append(recommendation)
    
    def get_recommendations(self) -> List[Dict]:
        """Retrieve all recommendations"""
        return self.recommendations


class CRAAgent(AgenticAI):
    """
    Clinical Research Associate Agent
    Monitors assigned sites and recommends actions
    """
    
    def __init__(self, cra_id: str, assigned_sites: List[str], generative_ai: Optional[GenerativeAI] = None):
        """
        Initialize CRA Agent
        
        Args:
            cra_id: CRA identifier
            assigned_sites: List of assigned site IDs
            generative_ai: GenerativeAI instance
        """
        super().__init__(cra_id, "Clinical Research Associate", generative_ai)
        self.assigned_sites = assigned_sites
    
    def analyze_site_backlog(self, site_metrics: Dict) -> List[Dict]:
        """
        Analyze site backlog and recommend actions
        
        Args:
            site_metrics: Dictionary of site-level metrics
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        for site_id in self.assigned_sites:
            if site_id in site_metrics:
                site = site_metrics[site_id]
                
                # Check for overdue visits
                if site.get("total_missing_visits", 0) > 5:
                    rec = {
                        "priority": "High",
                        "category": "Missing Visits",
                        "site_id": site_id,
                        "action": f"Schedule monitoring visit to site {site_id}",
                        "reason": f"{site['total_missing_visits']} missing visits require immediate attention",
                        "impact": "Patient data completeness at risk"
                    }
                    recommendations.append(rec)
                    self.log_recommendation(rec)
                
                # Check for query burden
                if site.get("total_open_queries", 0) > 20:
                    rec = {
                        "priority": "Medium",
                        "category": "Query Resolution",
                        "site_id": site_id,
                        "action": f"Conduct query resolution session with site {site_id}",
                        "reason": f"{site['total_open_queries']} open queries need resolution",
                        "impact": "Database lock timeline at risk"
                    }
                    recommendations.append(rec)
                    self.log_recommendation(rec)
                
                # Check for low performance
                if site.get("performance_score", 100) < 70:
                    rec = {
                        "priority": "High",
                        "category": "Site Performance",
                        "site_id": site_id,
                        "action": f"Escalate site {site_id} to Study Manager",
                        "reason": f"Performance score {site['performance_score']:.1f} below acceptable threshold",
                        "impact": "Study timelines and data quality at risk"
                    }
                    recommendations.append(rec)
                    self.log_recommendation(rec)
        
        logger.info(f"CRA Agent {self.agent_name} generated {len(recommendations)} recommendations")
        return recommendations
    
    def prioritize_monitoring_visits(self, site_metrics: Dict) -> List[Dict]:
        """
        Prioritize sites for monitoring visits
        
        Args:
            site_metrics: Dictionary of site-level metrics
            
        Returns:
            Prioritized list of sites for visits
        """
        visit_priorities = []
        
        for site_id in self.assigned_sites:
            if site_id in site_metrics:
                site = site_metrics[site_id]
                
                # Calculate urgency score
                urgency_score = 0
                
                if site.get("total_missing_visits", 0) > 0:
                    urgency_score += site["total_missing_visits"] * 5
                
                if site.get("total_open_queries", 0) > 0:
                    urgency_score += site["total_open_queries"] * 2
                
                if site.get("performance_score", 100) < 70:
                    urgency_score += 50
                
                visit_priorities.append({
                    "site_id": site_id,
                    "urgency_score": urgency_score,
                    "recommended_action": "Immediate visit" if urgency_score > 50 else "Routine visit",
                    "focus_areas": self._identify_visit_focus_areas(site)
                })
        
        # Sort by urgency
        visit_priorities.sort(key=lambda x: x["urgency_score"], reverse=True)
        
        logger.info(f"Prioritized {len(visit_priorities)} sites for monitoring visits")
        return visit_priorities
    
    def _identify_visit_focus_areas(self, site: Dict) -> List[str]:
        """Identify what to focus on during site visit"""
        focus_areas = []
        
        if site.get("total_missing_visits", 0) > 5:
            focus_areas.append("Visit completion and data entry")
        
        if site.get("total_open_queries", 0) > 15:
            focus_areas.append("Query resolution training")
        
        if site.get("total_missing_pages", 0) > 10:
            focus_areas.append("CRF completion procedures")
        
        return focus_areas if focus_areas else ["General monitoring"]


class DataQualityAgent(AgenticAI):
    """
    Data Quality Agent
    Monitors data quality across studies and recommends improvements
    """
    
    def __init__(self, generative_ai: Optional[GenerativeAI] = None):
        """Initialize Data Quality Agent"""
        super().__init__("DQAgent", "Data Quality Manager", generative_ai)
    
    def detect_systemic_issues(self, subject_metrics: pd.DataFrame) -> List[Dict]:
        """
        Detect systemic data quality issues
        
        Args:
            subject_metrics: DataFrame with subject-level metrics
            
        Returns:
            List of systemic issues detected
        """
        issues = []
        
        if subject_metrics is None or subject_metrics.empty:
            return issues
        
        # Detect high query rate
        if "open_queries" in subject_metrics.columns:
            avg_queries = subject_metrics["open_queries"].mean()
            if avg_queries > 3:
                issue = {
                    "priority": "High",
                    "category": "Systemic Query Issue",
                    "action": "Review query management processes",
                    "reason": f"Average of {avg_queries:.1f} open queries per subject",
                    "impact": "Indicates training gaps or systemic data collection issues",
                    "affected_entities": len(subject_metrics[subject_metrics["open_queries"] > 3])
                }
                issues.append(issue)
                self.log_recommendation(issue)
        
        # Detect widespread missing data
        if "pct_missing_pages" in subject_metrics.columns:
            high_missing = subject_metrics[subject_metrics["pct_missing_pages"] > 20]
            if len(high_missing) > len(subject_metrics) * 0.2:  # More than 20% of subjects
                issue = {
                    "priority": "High",
                    "category": "Data Completeness",
                    "action": "Audit CRF completion procedures across sites",
                    "reason": f"{len(high_missing)} subjects with >20% missing pages",
                    "impact": "Study-wide data collection issues",
                    "affected_entities": len(high_missing)
                }
                issues.append(issue)
                self.log_recommendation(issue)
        
        # Detect SDV backlog
        if "sdv_complete" in subject_metrics.columns:
            incomplete_sdv = subject_metrics[~subject_metrics["sdv_complete"]]
            if len(incomplete_sdv) > len(subject_metrics) * 0.3:  # More than 30% incomplete
                issue = {
                    "priority": "Medium",
                    "category": "SDV Backlog",
                    "action": "Increase SDV resources or adjust monitoring schedule",
                    "reason": f"{len(incomplete_sdv)} subjects with incomplete SDV",
                    "impact": "Monitoring timeline at risk",
                    "affected_entities": len(incomplete_sdv)
                }
                issues.append(issue)
                self.log_recommendation(issue)
        
        logger.info(f"Data Quality Agent detected {len(issues)} systemic issues")
        return issues
    
    def recommend_query_resolution_strategy(self, query_metrics: Dict) -> Dict:
        """
        Recommend strategy for query resolution
        
        Args:
            query_metrics: Query-related metrics
            
        Returns:
            Strategy recommendation
        """
        strategy = {
            "approach": "Standard resolution",
            "timeline": "Normal",
            "resource_allocation": "Current staffing",
            "specific_actions": []
        }
        
        total_queries = query_metrics.get("total_open_queries", 0)
        
        if total_queries > 100:
            strategy["approach"] = "Intensive resolution campaign"
            strategy["timeline"] = "Urgent - 2 weeks"
            strategy["resource_allocation"] = "Additional DM resources required"
            strategy["specific_actions"] = [
                "Daily query resolution calls with top 3 sites",
                "Escalate persistent queries to medical monitor",
                "Provide query resolution training to sites"
            ]
        elif total_queries > 50:
            strategy["approach"] = "Focused resolution effort"
            strategy["timeline"] = "Moderate - 4 weeks"
            strategy["resource_allocation"] = "Current staffing with overtime"
            strategy["specific_actions"] = [
                "Weekly query review meetings",
                "Prioritize safety-related queries",
                "Target sites with >10 open queries"
            ]
        
        self.log_recommendation(strategy)
        logger.info(f"Generated query resolution strategy for {total_queries} queries")
        return strategy


class TrialManagerAgent(AgenticAI):
    """
    Trial Manager Agent
    Monitors overall study health and readiness
    """
    
    def __init__(self, study_id: str, generative_ai: Optional[GenerativeAI] = None):
        """Initialize Trial Manager Agent"""
        super().__init__(f"TMAgent_{study_id}", "Trial Manager", generative_ai)
        self.study_id = study_id
    
    def assess_milestone_risk(self, study_metrics: Dict, milestone_name: str, 
                             target_date: datetime) -> Dict:
        """
        Assess risk of meeting a study milestone
        
        Args:
            study_metrics: Study-level metrics
            milestone_name: Name of milestone (e.g., "Database Lock")
            target_date: Target date for milestone
            
        Returns:
            Risk assessment
        """
        assessment = {
            "milestone": milestone_name,
            "target_date": target_date,
            "days_remaining": (target_date - datetime.now()).days,
            "risk_level": "Low",
            "confidence": "High",
            "blocking_issues": [],
            "recommendations": []
        }
        
        # Assess based on data cleanliness
        pct_clean = study_metrics.get("pct_clean", 0)
        if pct_clean < 75:
            assessment["risk_level"] = "High"
            assessment["blocking_issues"].append(f"Only {pct_clean:.1f}% clean patients")
            assessment["recommendations"].append("Initiate data cleaning campaign immediately")
        elif pct_clean < 90:
            assessment["risk_level"] = "Medium"
            assessment["recommendations"].append("Accelerate data cleaning activities")
        
        # Assess query burden
        total_queries = study_metrics.get("total_open_queries", 0)
        subjects = study_metrics.get("total_subjects", 1)
        queries_per_subject = total_queries / subjects
        
        if queries_per_subject > 2:
            if assessment["risk_level"] == "Low":
                assessment["risk_level"] = "Medium"
            assessment["blocking_issues"].append(f"{total_queries} open queries")
            assessment["recommendations"].append("Implement query resolution task force")
        
        # Assess safety events
        open_saes = study_metrics.get("open_saes", 0)
        if open_saes > 0:
            if assessment["risk_level"] == "Low":
                assessment["risk_level"] = "Medium"
            assessment["blocking_issues"].append(f"{open_saes} unresolved safety events")
            assessment["recommendations"].append("Prioritize SAE resolution before milestone")
        
        self.log_recommendation(assessment)
        logger.info(f"Assessed {milestone_name} risk: {assessment['risk_level']}")
        return assessment
    
    def recommend_resource_allocation(self, all_site_metrics: Dict) -> Dict:
        """
        Recommend how to allocate resources across sites
        
        Args:
            all_site_metrics: Metrics for all sites
            
        Returns:
            Resource allocation recommendation
        """
        allocation = {
            "high_priority_sites": [],
            "standard_monitoring_sites": [],
            "low_touch_sites": [],
            "recommended_cra_distribution": {}
        }
        
        for site_id, metrics in all_site_metrics.items():
            score = metrics.get("performance_score", 100)
            
            if score < 70:
                allocation["high_priority_sites"].append({
                    "site_id": site_id,
                    "score": score,
                    "recommended_visit_frequency": "Weekly"
                })
            elif score < 85:
                allocation["standard_monitoring_sites"].append({
                    "site_id": site_id,
                    "score": score,
                    "recommended_visit_frequency": "Bi-weekly"
                })
            else:
                allocation["low_touch_sites"].append({
                    "site_id": site_id,
                    "score": score,
                    "recommended_visit_frequency": "Monthly"
                })
        
        self.log_recommendation(allocation)
        logger.info(f"Generated resource allocation: {len(allocation['high_priority_sites'])} high-priority sites")
        return allocation
    
    def generate_executive_briefing(self, study_metrics: Dict, risk_report: Dict) -> str:
        """
        Generate executive briefing
        
        Args:
            study_metrics: Study-level metrics
            risk_report: Risk analysis report
            
        Returns:
            Executive briefing text
        """
        if self.generative_ai and self.generative_ai.client:
            briefing = self.generative_ai.summarize_study_performance(self.study_id, study_metrics)
        else:
            # Fallback briefing
            briefing = f"""Executive Briefing - {self.study_id}
            
Study Status:
- Total Subjects: {study_metrics.get('total_subjects', 0)}
- Clean Data Rate: {study_metrics.get('pct_clean', 0):.1f}%
- Open Queries: {study_metrics.get('total_open_queries', 0)}
- Safety Events: {study_metrics.get('open_saes', 0)} unresolved

Risk Summary:
- Critical Issues: {risk_report.get('risk_summary', {}).get('critical_issues_count', 0)}
- High-Risk Sites: {len(risk_report.get('risk_summary', {}).get('high_risk_sites', []))}

Recommendation: {'Proceed with caution' if study_metrics.get('pct_clean', 0) < 90 else 'On track'}
"""
        
        logger.info(f"Generated executive briefing for {self.study_id}")
        return briefing
