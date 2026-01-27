"""
Harmonization Module
Creates a unified canonical data model from heterogeneous sources
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from loguru import logger
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import COLUMN_MAPPINGS


class CanonicalDataModel:
    """
    Creates and manages the canonical data model across all trial data sources
    """
    
    def __init__(self):
        """Initialize the canonical data model"""
        self.entities = {
            "studies": pd.DataFrame(),
            "sites": pd.DataFrame(),
            "subjects": pd.DataFrame(),
            "visits": pd.DataFrame(),
            "queries": pd.DataFrame(),
            "safety_events": pd.DataFrame(),
            "lab_data": pd.DataFrame(),
            "coding_data": pd.DataFrame()
        }
        logger.info("Canonical Data Model initialized")
    
    def standardize_column_names(self, df: pd.DataFrame, entity_type: str) -> pd.DataFrame:
        """
        Standardize column names based on configuration mappings
        
        Args:
            df: Input DataFrame
            entity_type: Type of entity (for logging)
            
        Returns:
            DataFrame with standardized column names
        """
        if df is None or df.empty:
            return df
        
        df_copy = df.copy()
        renamed_cols = {}
        
        for standard_name, variations in COLUMN_MAPPINGS.items():
            for col in df_copy.columns:
                col_stripped = str(col).strip()
                # Check for exact matches or partial matches
                for variation in variations:
                    if variation.lower() in col_stripped.lower() or col_stripped.lower() in variation.lower():
                        if col not in renamed_cols:  # Avoid renaming same column twice
                            renamed_cols[col] = standard_name
                            logger.debug(f"Renamed '{col}' to '{standard_name}' in {entity_type}")
                        break
                if col in renamed_cols:
                    break
        
        df_copy.rename(columns=renamed_cols, inplace=True)
        return df_copy
    
    def extract_study_entity(self, all_data: Dict[str, Dict[str, pd.DataFrame]]) -> pd.DataFrame:
        """
        Extract study-level entity from all data sources
        
        Args:
            all_data: Nested dictionary of all ingested data
            
        Returns:
            DataFrame with study-level information
        """
        studies = []
        
        for study_name, study_data in all_data.items():
            study_record = {
                "study_id": study_name,
                "study_name": study_name,
                "data_sources": len(study_data),
                "has_edc": "edc_metrics" in study_data,
                "has_safety": "sae_dashboard" in study_data,
                "has_coding": any("coding" in k for k in study_data.keys()),
                "has_lab": "lab_report" in study_data
            }
            studies.append(study_record)
        
        self.entities["studies"] = pd.DataFrame(studies)
        logger.info(f"Extracted {len(studies)} study entities")
        return self.entities["studies"]
    
    def extract_site_entity(self, all_data: Dict[str, Dict[str, pd.DataFrame]]) -> pd.DataFrame:
        """
        Extract site-level entity from all data sources
        
        Args:
            all_data: Nested dictionary of all ingested data
            
        Returns:
            DataFrame with site-level information
        """
        sites = []
        
        for study_name, study_data in all_data.items():
            # Extract from EDC metrics
            if "edc_metrics" in study_data:
                edc_df = self.standardize_column_names(study_data["edc_metrics"], "edc_metrics")
                
                if "site_id" in edc_df.columns:
                    site_cols = ["site_id"]
                    optional_cols = ["region", "country"]
                    
                    for col in optional_cols:
                        if col in edc_df.columns:
                            site_cols.append(col)
                    
                    site_df = edc_df[site_cols].drop_duplicates()
                    site_df["study_id"] = study_name
                    
                    sites.append(site_df)
        
        if sites:
            self.entities["sites"] = pd.concat(sites, ignore_index=True)
            logger.info(f"Extracted {len(self.entities['sites'])} site entities")
        
        return self.entities["sites"]
    
    def extract_subject_entity(self, all_data: Dict[str, Dict[str, pd.DataFrame]]) -> pd.DataFrame:
        """
        Extract subject-level entity from all data sources
        
        Args:
            all_data: Nested dictionary of all ingested data
            
        Returns:
            DataFrame with subject-level information
        """
        subjects = []
        
        for study_name, study_data in all_data.items():
            if "edc_metrics" in study_data:
                edc_df = self.standardize_column_names(study_data["edc_metrics"], "edc_metrics")
                
                if "subject_id" in edc_df.columns:
                    subject_cols = ["subject_id", "site_id"]
                    optional_cols = ["status", "region", "country"]
                    
                    for col in optional_cols:
                        if col in edc_df.columns:
                            subject_cols.append(col)
                    
                    # Get unique columns that exist
                    existing_cols = [col for col in subject_cols if col in edc_df.columns]
                    
                    if existing_cols:
                        subject_df = edc_df[existing_cols].drop_duplicates()
                        subject_df["study_id"] = study_name
                        subjects.append(subject_df)
        
        if subjects:
            self.entities["subjects"] = pd.concat(subjects, ignore_index=True)
            logger.info(f"Extracted {len(self.entities['subjects'])} subject entities")
        
        return self.entities["subjects"]
    
    def extract_visit_entity(self, all_data: Dict[str, Dict[str, pd.DataFrame]]) -> pd.DataFrame:
        """
        Extract visit-level entity from all data sources
        
        Args:
            all_data: Nested dictionary of all ingested data
            
        Returns:
            DataFrame with visit-level information
        """
        visits = []
        
        for study_name, study_data in all_data.items():
            # Extract from missing pages report
            if "missing_pages" in study_data:
                pages_df = self.standardize_column_names(study_data["missing_pages"], "missing_pages")
                
                required_cols = ["subject_id", "visit_name"]
                if all(col in pages_df.columns for col in required_cols):
                    visit_df = pages_df[required_cols].drop_duplicates()
                    visit_df["study_id"] = study_name
                    visit_df["has_missing_data"] = True
                    visits.append(visit_df)
        
        if visits:
            self.entities["visits"] = pd.concat(visits, ignore_index=True)
            logger.info(f"Extracted {len(self.entities['visits'])} visit entities")
        
        return self.entities["visits"]
    
    def extract_safety_entity(self, all_data: Dict[str, Dict[str, pd.DataFrame]]) -> pd.DataFrame:
        """
        Extract safety event entity from all data sources
        
        Args:
            all_data: Nested dictionary of all ingested data
            
        Returns:
            DataFrame with safety event information
        """
        safety_events = []
        
        for study_name, study_data in all_data.items():
            if "sae_dashboard" in study_data:
                sae_df = self.standardize_column_names(study_data["sae_dashboard"], "sae_dashboard")
                sae_df["study_id"] = study_name
                safety_events.append(sae_df)
        
        if safety_events:
            self.entities["safety_events"] = pd.concat(safety_events, ignore_index=True)
            logger.info(f"Extracted {len(self.entities['safety_events'])} safety event entities")
        
        return self.entities["safety_events"]
    
    def build_canonical_model(self, all_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Build the complete canonical data model from all sources
        
        Args:
            all_data: Dictionary mapping study names to consolidated DataFrames
            
        Returns:
            Dictionary of canonical entities (subjects, sites, studies)
        """
        logger.info("Building canonical data model from consolidated data...")
        
        # Data is already consolidated at subject level, just extract entities
        subjects = []
        sites = []
        studies = []
        
        for study_name, study_df in all_data.items():
            if study_df is not None and not study_df.empty:
                # Extract subjects
                if "subject_id" in study_df.columns:
                    subject_cols = ["subject_id", "site_id"]
                    if "country" in study_df.columns:
                        subject_cols.append("country")
                    
                    existing_cols = [col for col in subject_cols if col in study_df.columns]
                    if existing_cols:
                        subject_df = study_df[existing_cols].drop_duplicates()
                        subject_df["study_id"] = study_name
                        subjects.append(subject_df)
                
                # Extract sites
                if "site_id" in study_df.columns:
                    site_cols = ["site_id"]
                    if "country" in study_df.columns:
                        site_cols.append("country")
                    
                    existing_cols = [col for col in site_cols if col in study_df.columns]
                    if existing_cols:
                        site_df = study_df[existing_cols].drop_duplicates()
                        site_df["study_id"] = study_name
                        sites.append(site_df)
                
                # Study entity
                studies.append({
                    "study_id": study_name,
                    "subject_count": len(study_df)
                })
        
        # Consolidate entities
        if subjects:
            self.entities["subjects"] = pd.concat(subjects, ignore_index=True)
            logger.info(f"Extracted {len(self.entities['subjects'])} subject entities")
        else:
            self.entities["subjects"] = pd.DataFrame()
        
        if sites:
            self.entities["sites"] = pd.concat(sites, ignore_index=True)
            logger.info(f"Extracted {len(self.entities['sites'])} site entities")
        else:
            self.entities["sites"] = pd.DataFrame()
        
        if studies:
            self.entities["studies"] = pd.DataFrame(studies)
            logger.info(f"Extracted {len(self.entities['studies'])} study entities")
        else:
            self.entities["studies"] = pd.DataFrame()
        
        # No need to extract visits or safety entities separately - they're already in the data
        
        return self.entities
    
    def get_entity(self, entity_name: str) -> Optional[pd.DataFrame]:
        """
        Retrieve a specific entity from the canonical model
        
        Args:
            entity_name: Name of the entity
            
        Returns:
            DataFrame or None if entity doesn't exist
        """
        return self.entities.get(entity_name)
    
    def get_unified_patient_view(self, study_id: str, subject_id: str) -> Dict:
        """
        Get a complete unified view of a single patient
        
        Args:
            study_id: Study identifier
            subject_id: Subject identifier
            
        Returns:
            Dictionary containing all patient information
        """
        patient_view = {
            "study_id": study_id,
            "subject_id": subject_id
        }
        
        # Get subject info
        subjects = self.entities["subjects"]
        if not subjects.empty:
            subject_data = subjects[
                (subjects["study_id"] == study_id) & 
                (subjects["subject_id"] == subject_id)
            ]
            if not subject_data.empty:
                patient_view.update(subject_data.iloc[0].to_dict())
        
        # Get visits
        visits = self.entities["visits"]
        if not visits.empty:
            visit_data = visits[
                (visits["study_id"] == study_id) & 
                (visits["subject_id"] == subject_id)
            ]
            patient_view["visits"] = visit_data.to_dict("records")
        
        # Get safety events
        safety = self.entities["safety_events"]
        if not safety.empty and "subject_id" in safety.columns:
            safety_data = safety[
                (safety["study_id"] == study_id) & 
                (safety["subject_id"] == subject_id)
            ]
            patient_view["safety_events"] = safety_data.to_dict("records")
        
        return patient_view
