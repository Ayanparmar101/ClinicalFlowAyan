"""
Configuration module for the Clinical Trial Intelligence Platform
"""
import os
from pathlib import Path
from dotenv import load_dotenv

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data"
OUTPUT_PATH = BASE_DIR / "output"
LOGS_PATH = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_PATH.mkdir(exist_ok=True)
OUTPUT_PATH.mkdir(exist_ok=True)
LOGS_PATH.mkdir(exist_ok=True)

# Application Configuration
APP_NAME = os.getenv("APP_NAME", "Clinical Trial Intelligence Platform")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Gemini API Configuration
# Try Streamlit secrets first (for hosted deployment), then fall back to .env
def get_gemini_api_key():
    """Get Gemini API key from Streamlit secrets or environment"""
    if HAS_STREAMLIT:
        try:
            return st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
        except Exception:
            return os.getenv("GEMINI_API_KEY", "")
    return os.getenv("GEMINI_API_KEY", "")

GEMINI_API_KEY = get_gemini_api_key()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemma-3-27b-it")
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.3"))
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "2000"))

# Data Quality Index Weights
DQI_WEIGHTS = {
    "safety_issues": 0.35,      # Highest priority
    "missing_visits": 0.25,
    "open_queries": 0.20,
    "missing_pages": 0.10,
    "coding_delays": 0.05,
    "sdv_incomplete": 0.05
}

# Risk Thresholds
RISK_THRESHOLDS = {
    "high": 70,    # Score below 70 = High Risk
    "medium": 85   # Score 70-85 = Medium Risk, above 85 = Low Risk
}

# Clean Patient Criteria
CLEAN_PATIENT_CRITERIA = {
    "missing_visits": 0,
    "missing_pages": 0,
    "open_queries": 0,
    "pending_sdv": 0,
    "open_safety_issues": 0
}

# File Type Mappings
FILE_TYPE_PATTERNS = {
    "edc_metrics": "*EDC_Metrics*.xlsx",
    "missing_pages": "*Missing_Pages*.xlsx",
    "sae_dashboard": "*SAE*.xlsx",
    "coding_report": "*Coding*.xlsx",
    "lab_report": "*Lab*.xlsx",
    "visit_projection": "*Visit_Projection*.xlsx",
    "inactivated_forms": "*Inactivated*.xlsx",
    "edrr": "*EDRR*.xlsx"
}

# Column Standardization Mappings
COLUMN_MAPPINGS = {
    "subject_id": ["Subject ID", "Subject", "SubjectID", "Patient ID", "SUBJID", "subject_id"],
    "site_id": ["Site ID", "Site", "SiteID", "Site Number", "site_id"],
    "study_id": ["Study ID", "Study", "StudyID", "Protocol", "Project Name"],
    "visit_name": ["Visit", "Visit Name", "VisitName", "Latest Visit"],
    "region": ["Region"],
    "country": ["Country"],
    "status": ["Status", "Subject Status", "SubjectStatus"],
    
    # EDC Metrics specific mappings
    "missing_visits": ["Missing Visits", "Input files - Missing Visits"],
    "missing_pages": ["Missing Page", "Missing Pages", "Input files - Missing Page"],
    "open_queries": ["# Open Queries", "Open Queries", "#Total Queries", "# DM Queries", "Total Queries"],
    "closed_queries": ["# Closed Queries", "Closed Queries"],
    "total_queries": ["#Total Queries", "Total Queries", "#Total"],
    "coded_terms": ["# Coded terms", "Coded terms"],
    "uncoded_terms": ["# Uncoded Terms", "Uncoded Terms"],
    "open_lnr_issues": ["# Open issues in LNR", "Open LNR"],
    "inactivated_forms": ["Inactivated forms and folders", "Inactivated Forms"],
    "sae_review": ["# eSAE dashboard review for DM", "SAE Review"],
    "broken_signatures": ["Broken Signatures"],
    "never_signed": ["CRFs Never Signed", "Never Signed"],
    "pages_entered": ["# Pages Entered", "Pages Entered"],
    "expected_visits": ["# Expected Visits", "Expected Visits"],
    "forms_verified": ["# Forms Verified", "Forms Verified"],
    "crfs_frozen": ["# CRFs Frozen", "CRFs Frozen"],
    "crfs_locked": ["# CRFs Locked", "CRFs Locked"]
}
