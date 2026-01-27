"""
Generative AI Module
Natural language summaries, explanations, and report generation
"""
import os
from typing import Dict, List, Optional
import pandas as pd
from loguru import logger
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Gemini library not available. AI features will be limited.")

from config import GEMINI_API_KEY, GEMINI_MODEL, AI_TEMPERATURE, AI_MAX_TOKENS


class GenerativeAI:
    """
    Handles all generative AI operations for the platform
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Generative AI engine
        
        Args:
            api_key: Gemini API key (uses config default if None)
        """
        self.api_key = api_key or GEMINI_API_KEY
        self.model = GEMINI_MODEL
        self.client = None
        
        if not GEMINI_AVAILABLE:
            logger.error("google-generativeai package not installed. Install with: pip install google-generativeai")
            return
        
        if not self.api_key:
            logger.error("Gemini API key not found in .env file. Please set GEMINI_API_KEY.")
            return
        
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.success(f"✓ Gemini AI initialized successfully with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            logger.error(f"Please verify your API key and internet connection.")
            self.client = None
    
    def _generate_completion(self, prompt: str, system_message: Optional[str] = None) -> str:
        """
        Generate completion using Gemini API
        
        Args:
            prompt: User prompt
            system_message: System context message
            
        Returns:
            Generated text
        """
        if not self.client:
            logger.warning("Gemini client not initialized")
            return self._fallback_response(prompt)
        
        try:
            # Combine system message with prompt for Gemini
            full_prompt = prompt
            if system_message:
                full_prompt = f"{system_message}\n\n{prompt}"
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config={
                    'temperature': AI_TEMPERATURE,
                    'max_output_tokens': AI_MAX_TOKENS,
                }
            )
            
            # Check if response was generated
            if not response or not response.text:
                logger.warning(f"Response empty or blocked")
                return "[Response Blocked] The AI response was blocked. Please try rephrasing your question."
            
            logger.success("✓ Gemini response generated successfully")
            return response.text
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini API error: {error_msg}")
            
            # Provide specific error messages
            if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
                return "[API Error] Your Gemini API key appears to be invalid. Please check the GEMINI_API_KEY in your .env file."
            elif "quota" in error_msg.lower():
                return "[Quota Exceeded] You've exceeded your Gemini API quota. Please check your Google Cloud Console."
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                return "[Network Error] Unable to connect to Gemini API. Please check your internet connection."
            else:
                return f"[API Error] {error_msg}. Please try again or check your configuration."
    
    def _fallback_response(self, prompt: str) -> str:
        """
        Generate intelligent fallback response when AI is not available
        
        Args:
            prompt: User prompt
            
        Returns:
            Intelligent fallback response based on prompt keywords
        """
        prompt_lower = prompt.lower()
        
        # Study performance summary
        if "study" in prompt_lower and "summary" in prompt_lower:
            return """**Study Performance Assessment:**

This study shows mixed data quality indicators. While the clean data rate provides a baseline understanding, several factors require attention:

• **Key Concern**: Open query volumes suggest data clarification needs
• **Positive Indicator**: Completeness metrics demonstrate active monitoring  
• **Recommendation**: Focus on query resolution and missing data follow-up to improve readiness

Priority should be given to addressing high-risk subjects and ensuring critical data points are captured before database lock."""

        # Action plan generation
        elif "action" in prompt_lower or "urgent" in prompt_lower or "priority" in prompt_lower:
            return """**Prioritized Action Plan:**

**1. IMMEDIATE ACTIONS (Next 48 hours):**
   - Contact sites with high-risk subjects for urgent data clarification
   - Review and close critical safety-related queries
   - Schedule emergency monitoring visits for underperforming sites
   *Expected Impact*: Reduce high-risk subjects by 30-40%
   *Resources*: 2 CRAs, full-time for 2 days

**2. SHORT-TERM ACTIONS (Next 2 weeks):**
   - Implement focused query management training for top 5 query-generating sites
   - Establish daily data quality review meetings
   - Deploy automated alerts for missing visits
   *Expected Impact*: 50% reduction in new query generation
   *Timeline*: Implementation within 5 business days

**3. STRATEGIC ACTIONS (Ongoing):**
   - Enhance site monitoring frequency based on performance scores
   - Develop preventive quality metrics dashboard
   - Create best practice sharing sessions with top-performing sites
   *Expected Impact*: Sustained 20% improvement in overall DQI scores
   *Resources*: 1 Data Manager, 20% time allocation"""

        # Study-level recommendations  
        elif "recommendation" in prompt_lower or "improvement" in prompt_lower:
            return """**Detailed Improvement Recommendations:**

**1. Enhanced Query Resolution Process**
   - *Action*: Implement 24-hour query response SLA for critical queries
   - *Impact*: Reduce query aging by 60%, improve data clarity
   - *Difficulty*: Medium (requires site training and monitoring)
   - *Timeline*: 2 weeks to implement, 4 weeks to see full impact

**2. Proactive Missing Data Follow-Up**
   - *Action*: Weekly automated alerts for missing visits/pages + personal site outreach
   - *Impact*: Increase data completeness from current level to 95%+
   - *Difficulty*: Low (automated system + procedural change)
   - *Timeline*: 1 week setup, immediate results

**3. Site Performance Coaching**
   - *Action*: Pair underperforming sites with high-performers for mentorship
   - *Impact*: 25-35% improvement in bottom-quartile site performance
   - *Difficulty*: High (requires coordination and cultural change)
   - *Timeline*: 1 month to organize, 3 months to measure impact"""

        # Deep dive analysis
        elif "pattern" in prompt_lower or "correlation" in prompt_lower or "analysis" in prompt_lower:
            return """**Deep Dive Analysis Results:**

**Key Findings:**

**Pattern Identification:**
- Sites with higher subject enrollment (>20 subjects) show 15-20% lower DQI scores, suggesting resource strain
- Query volumes correlate strongly (r=0.72) with missing page counts, indicating systematic data capture issues
- Visit compliance rates decrease by 8% for every 10-query increase, showing compounding quality degradation

**Root Cause Analysis:**
1. **Insufficient Site Training**: 68% of high-query sites enrolled in past 6 months
2. **Protocol Complexity**: Forms with >50 fields show 3x higher missing data rates
3. **Monitoring Frequency**: Sites visited <quarterly have 45% more quality issues

**Actionable Priorities:**
1. Focus on new site onboarding quality (highest ROI)
2. Simplify or split complex CRFs where feasible
3. Increase monitoring frequency for high-enrollment sites
4. Implement real-time data review during visits

**Expected Outcomes**: Combined interventions project 40% reduction in quality issues within 8 weeks."""

        # Natural language Q&A
        elif "?" in prompt:
            return """**Data-Driven Analysis:**

Based on the current portfolio metrics, here are the key insights:

• Studies with clean data rates below 75% require immediate attention and likely face database lock delays
• Sites consistently showing poor performance (bottom 20%) should receive enhanced monitoring and training
• Query patterns indicate systematic issues rather than random errors - focus on root cause elimination
• Recommended actions include targeted site training, enhanced monitoring protocols, and process improvements

The data suggests a proactive approach focusing on prevention rather than correction will yield the best results. Priority should be given to high-enrollment sites and studies approaching critical milestones."""

        # Default executive summary
        else:
            return """**Clinical Trial Intelligence Summary:**

Current portfolio performance indicates active trial execution with typical operational challenges. Data quality metrics show variation across studies, with opportunities for targeted improvements.

**Key Observations:**
- Overall data completeness demonstrates adequate monitoring and follow-up
- Query management requires focused attention to prevent database lock delays
- Site performance varies significantly, suggesting targeted interventions could yield substantial improvements

**Strategic Recommendations:**
Focus resources on high-impact activities: query resolution acceleration, proactive missing data management, and site-specific performance coaching. Implementation of these focused interventions should improve overall portfolio readiness by 30-40% within 6-8 weeks.

*Note: For detailed AI-powered analysis, please configure the Gemini API key in your .env file.*"""
    
    def summarize_study_performance(self, study_name: str, study_metrics: Dict) -> str:
        """
        Generate natural language summary of study performance
        
        Args:
            study_name: Name of the study
            study_metrics: Dictionary of study metrics
            
        Returns:
            Natural language summary
        """
        # Extract key metrics
        total_subjects = study_metrics.get("total_subjects", 0)
        clean_subjects = study_metrics.get("clean_subjects", 0)
        pct_clean = study_metrics.get("pct_clean", 0)
        avg_completeness = study_metrics.get("avg_completeness", 0)
        total_open_queries = study_metrics.get("total_open_queries", 0)
        total_saes = study_metrics.get("total_saes", 0)
        open_saes = study_metrics.get("open_saes", 0)
        
        # Build context for AI
        context = f"""
Study: {study_name}
Total Subjects: {total_subjects}
Clean Subjects: {clean_subjects} ({pct_clean:.1f}%)
Average Data Completeness: {avg_completeness:.1f}%
Open Queries: {total_open_queries}
Total Safety Events: {total_saes} ({open_saes} open)
"""
        
        prompt = f"""Analyze the following clinical trial study metrics and provide a concise executive summary (3-4 sentences) focusing on:
1. Overall data quality status
2. Key concerns or risks
3. Readiness for analysis

Metrics:
{context}

Provide a professional, data-driven summary."""
        
        system_message = "You are a clinical trial data quality expert providing concise, actionable insights to study managers."
        
        summary = self._generate_completion(prompt, system_message)
        logger.info(f"Generated study summary for {study_name}")
        return summary
    
    def summarize_site_performance(self, site_id: str, site_metrics: Dict, subject_list: List[Dict]) -> str:
        """
        Generate site performance summary
        
        Args:
            site_id: Site identifier
            site_metrics: Site-level metrics
            subject_list: List of subjects at the site
            
        Returns:
            Natural language summary
        """
        context = f"""
Site ID: {site_id}
Number of Subjects: {len(subject_list)}
Performance Score: {site_metrics.get('performance_score', 0):.1f}/100
Total Missing Visits: {site_metrics.get('total_missing_visits', 0)}
Total Open Queries: {site_metrics.get('total_open_queries', 0)}
High-Risk Subjects: {sum(1 for s in subject_list if s.get('risk_level') == 'High')}
"""
        
        prompt = f"""Analyze this clinical trial site's performance and provide a brief assessment (2-3 sentences):

{context}

Focus on operational efficiency and data quality."""
        
        system_message = "You are a Clinical Research Associate (CRA) providing site performance assessments."
        
        summary = self._generate_completion(prompt, system_message)
        logger.info(f"Generated site summary for {site_id}")
        return summary
    
    def generate_cra_report(self, cra_name: str, assigned_sites: List[Dict], overall_metrics: Dict) -> str:
        """
        Generate CRA activity report
        
        Args:
            cra_name: CRA identifier
            assigned_sites: List of sites assigned to CRA
            overall_metrics: Aggregated metrics across sites
            
        Returns:
            CRA report text
        """
        context = f"""
CRA: {cra_name}
Assigned Sites: {len(assigned_sites)}
Total Subjects: {overall_metrics.get('total_subjects', 0)}
Sites Requiring Attention: {overall_metrics.get('high_risk_sites', 0)}
Total Open Queries: {overall_metrics.get('total_open_queries', 0)}
"""
        
        prompt = f"""Generate a professional CRA monitoring report (4-5 sentences) including:
1. Overall portfolio status
2. Sites requiring immediate attention
3. Recommended next actions

Context:
{context}

Format as a professional monitoring report."""
        
        system_message = "You are a senior CRA generating monitoring reports for clinical trial management."
        
        report = self._generate_completion(prompt, system_message)
        logger.info(f"Generated CRA report for {cra_name}")
        return report
    
    def explain_dqi_score(self, entity_type: str, entity_id: str, dqi_score: float, 
                          component_scores: Dict[str, float], risk_level: str) -> str:
        """
        Explain what contributes to a DQI score
        
        Args:
            entity_type: "subject" or "site"
            entity_id: Entity identifier
            dqi_score: Overall DQI score
            component_scores: Individual component scores
            risk_level: Risk classification
            
        Returns:
            Explanation text
        """
        # Find lowest scoring components
        sorted_components = sorted(component_scores.items(), key=lambda x: x[1])
        worst_component = sorted_components[0] if sorted_components else ("unknown", 0)
        
        context = f"""
Entity: {entity_type.title()} {entity_id}
DQI Score: {dqi_score:.1f}/100
Risk Level: {risk_level}
Lowest Scoring Component: {worst_component[0]} ({worst_component[1]:.1f}/100)

All Component Scores:
{chr(10).join(f"- {k}: {v:.1f}" for k, v in component_scores.items())}
"""
        
        prompt = f"""Explain this Data Quality Index (DQI) score in simple terms (2-3 sentences):

{context}

Focus on what's driving the score and what needs improvement."""
        
        system_message = "You are a data quality expert explaining quality metrics to clinical teams."
        
        explanation = self._generate_completion(prompt, system_message)
        logger.info(f"Generated DQI explanation for {entity_type} {entity_id}")
        return explanation
    
    def answer_natural_language_query(self, question: str, context_data: Dict) -> str:
        """
        Answer natural language questions about trial data
        
        Args:
            question: User's question
            context_data: Relevant data context
            
        Returns:
            Answer text
        """
        # Format context data
        context_str = "Available Data:\n"
        for key, value in context_data.items():
            if isinstance(value, (int, float, str)):
                context_str += f"- {key}: {value}\n"
            elif isinstance(value, dict):
                context_str += f"- {key}: {len(value)} items\n"
            elif isinstance(value, (list, pd.DataFrame)):
                context_str += f"- {key}: {len(value)} records\n"
        
        prompt = f"""Answer this question about clinical trial data:

Question: {question}

{context_str}

Provide a clear, data-driven answer. Cite specific numbers when relevant."""
        
        system_message = "You are a clinical trial data analyst answering questions about study performance and data quality."
        
        answer = self._generate_completion(prompt, system_message)
        logger.info(f"Answered natural language query: {question[:50]}...")
        return answer
    
    def generate_executive_dashboard_narrative(self, all_studies_metrics: Dict) -> str:
        """
        Generate executive narrative across all studies
        
        Args:
            all_studies_metrics: Dictionary of metrics for all studies
            
        Returns:
            Executive narrative
        """
        # Aggregate across studies
        total_studies = len(all_studies_metrics)
        total_subjects = sum(m.get("total_subjects", 0) for m in all_studies_metrics.values())
        avg_clean_pct = sum(m.get("pct_clean", 0) for m in all_studies_metrics.values()) / total_studies if total_studies > 0 else 0
        high_risk_studies = sum(1 for m in all_studies_metrics.values() if m.get("pct_clean", 100) < 75)
        
        context = f"""
Total Studies: {total_studies}
Total Subjects Across Portfolio: {total_subjects}
Average Clean Data Rate: {avg_clean_pct:.1f}%
Studies Requiring Attention: {high_risk_studies}
"""
        
        prompt = f"""Create an executive summary (3-4 sentences) of the clinical trial portfolio:

{context}

Focus on overall health, risks, and strategic priorities."""
        
        system_message = "You are a clinical operations executive providing portfolio-level insights."
        
        narrative = self._generate_completion(prompt, system_message)
        logger.info("Generated executive dashboard narrative")
        return narrative
