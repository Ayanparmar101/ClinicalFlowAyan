"""
Multi-File Data Loader - Loads clinical trial metrics from multiple specialized Excel files
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional
from loguru import logger


class MultiFileDataLoader:
    """
    Loads clinical trial data from multiple specialized files per study
    and consolidates into a unified subject-level dataset
    """
    
    def __init__(self, data_directory: Path):
        """Initialize with data directory path"""
        self.data_directory = Path(data_directory)
        logger.info(f"MultiFileDataLoader initialized with directory: {data_directory}")
    
    def load_study_data(self, study_name: str) -> Optional[pd.DataFrame]:
        """
        Load all data files for a study and consolidate at subject level
        
        Args:
            study_name: Name of the study folder
            
        Returns:
            DataFrame with consolidated subject-level metrics
        """
        study_path = self.data_directory / study_name
        
        if not study_path.exists():
            logger.error(f"Study path does not exist: {study_path}")
            return None
        
        logger.info(f"Loading data for {study_name}")
        
        # Load each specialized file
        missing_pages_df = self._load_missing_pages(study_path)
        missing_visits_df = self._load_missing_visits(study_path)
        edrr_df = self._load_edrr_issues(study_path)
        sae_df = self._load_sae_issues(study_path)
        coding_df = self._load_coding_issues(study_path)
        
        # Get all unique subjects from all files
        all_subjects = set()
        for df in [missing_pages_df, missing_visits_df, edrr_df, sae_df, coding_df]:
            if df is not None and not df.empty:
                subject_col = self._find_subject_column(df)
                if subject_col:
                    all_subjects.update(df[subject_col].unique())
        
        if not all_subjects:
            logger.warning(f"No subjects found for {study_name}")
            return None
        
        logger.info(f"Found {len(all_subjects)} unique subjects in {study_name}")
        
        # Build consolidated DataFrame
        consolidated = self._consolidate_subject_data(
            study_name,
            list(all_subjects),
            missing_pages_df,
            missing_visits_df,
            edrr_df,
            sae_df,
            coding_df,
            study_path
        )
        
        logger.info(f"Consolidated {len(consolidated)} subjects for {study_name}")
        return consolidated
    
    def _find_subject_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the subject column name (handles variations)"""
        for col in df.columns:
            col_lower = col.lower()
            if 'subject' in col_lower and 'status' not in col_lower:
                return col
        return None
    
    def _find_site_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the site column name (handles variations)"""
        for col in df.columns:
            col_lower = col.lower()
            if 'site' in col_lower and ('number' in col_lower or 'id' in col_lower or col_lower == 'site'):
                return col
        return None
    
    def _load_missing_pages(self, study_path: Path) -> Optional[pd.DataFrame]:
        """Load missing pages report"""
        try:
            files = list(study_path.glob('*Missing_Pages*.xlsx'))
            if not files:
                logger.debug(f"No missing pages file found in {study_path.name}")
                return None
            
            df = pd.read_excel(files[0])
            logger.debug(f"Loaded missing pages: {len(df)} rows from {files[0].name}")
            return df
        except Exception as e:
            logger.error(f"Error loading missing pages: {e}")
            return None
    
    def _load_missing_visits(self, study_path: Path) -> Optional[pd.DataFrame]:
        """Load visit projection tracker"""
        try:
            files = list(study_path.glob('*Visit*Projection*.xlsx'))
            if not files:
                logger.debug(f"No visit projection file found in {study_path.name}")
                return None
            
            df = pd.read_excel(files[0])
            
            # Handle files with header rows
            if 'Unnamed' in str(df.columns[0]) or 'Restricted' in str(df.iloc[0, 0]):
                # Try reading with different header row
                df = pd.read_excel(files[0], skiprows=2)
            
            # Check if actually has data
            if len(df) == 0 or df.columns[0].startswith('Unnamed'):
                logger.debug(f"Visit projection file is empty or malformed: {files[0].name}")
                return None
            
            logger.debug(f"Loaded visit projections: {len(df)} rows from {files[0].name}")
            return df
        except Exception as e:
            logger.error(f"Error loading visit projections: {e}")
            return None
    
    def _load_edrr_issues(self, study_path: Path) -> Optional[pd.DataFrame]:
        """Load EDRR compiled issues"""
        try:
            files = list(study_path.glob('*EDRR*.xlsx'))
            if not files:
                logger.debug(f"No EDRR file found in {study_path.name}")
                return None
            
            df = pd.read_excel(files[0])
            logger.debug(f"Loaded EDRR issues: {len(df)} rows from {files[0].name}")
            return df
        except Exception as e:
            logger.error(f"Error loading EDRR issues: {e}")
            return None
    
    def _load_sae_issues(self, study_path: Path) -> Optional[pd.DataFrame]:
        """Load SAE dashboard issues"""
        try:
            files = list(study_path.glob('*SAE*.xlsx'))
            if not files:
                logger.debug(f"No SAE file found in {study_path.name}")
                return None
            
            df = pd.read_excel(files[0])
            logger.debug(f"Loaded SAE issues: {len(df)} rows from {files[0].name}")
            return df
        except Exception as e:
            logger.error(f"Error loading SAE issues: {e}")
            return None
    
    def _load_coding_issues(self, study_path: Path) -> Optional[pd.DataFrame]:
        """Load coding reports (MedDRA + WHODrug)"""
        try:
            # Load both coding reports
            meddra_files = list(study_path.glob('*MedDRA*.xlsx'))
            whodd_files = list(study_path.glob('*WHODD*.xlsx'))
            
            dfs = []
            if meddra_files:
                df = pd.read_excel(meddra_files[0])
                dfs.append(df)
                logger.debug(f"Loaded MedDRA coding: {len(df)} rows")
            
            if whodd_files:
                df = pd.read_excel(whodd_files[0])
                dfs.append(df)
                logger.debug(f"Loaded WHODrug coding: {len(df)} rows")
            
            if dfs:
                return pd.concat(dfs, ignore_index=True)
            return None
        except Exception as e:
            logger.error(f"Error loading coding reports: {e}")
            return None
    
    def _consolidate_subject_data(
        self,
        study_name: str,
        subjects: list,
        missing_pages_df: Optional[pd.DataFrame],
        missing_visits_df: Optional[pd.DataFrame],
        edrr_df: Optional[pd.DataFrame],
        sae_df: Optional[pd.DataFrame],
        coding_df: Optional[pd.DataFrame],
        study_path: Path
    ) -> pd.DataFrame:
        """
        Consolidate all data sources into subject-level metrics
        """
        rows = []
        
        for subject in subjects:
            row = {
                'study_id': study_name,
                'subject_id': subject,
                'site_id': None,
                'region': None,
                'country': None,
                'missing_pages': 0,
                'missing_visits': 0,
                'open_queries': 0,  # Will aggregate from multiple sources
                'coded_terms': 0,
                'uncoded_terms': 0,
                'open_lnr_issues': 0,
                'sae_review': 0,
                'inactivated_forms': 0
            }
            
            # Extract site/region/country from missing pages (most complete)
            if missing_pages_df is not None and not missing_pages_df.empty:
                subject_col = self._find_subject_column(missing_pages_df)
                site_col = self._find_site_column(missing_pages_df)
                
                if subject_col:
                    subject_data = missing_pages_df[missing_pages_df[subject_col] == subject]
                    if not subject_data.empty:
                        if site_col:
                            row['site_id'] = subject_data.iloc[0][site_col]
                        if 'Country' in subject_data.columns or 'SiteGroupName(CountryName)' in subject_data.columns:
                            country_col = 'SiteGroupName(CountryName)' if 'SiteGroupName(CountryName)' in subject_data.columns else 'Country'
                            row['country'] = subject_data.iloc[0][country_col]
                        
                        # Count missing pages
                        row['missing_pages'] = len(subject_data)
            
            # Extract missing visits
            if missing_visits_df is not None and not missing_visits_df.empty:
                subject_col = self._find_subject_column(missing_visits_df)
                if subject_col:
                    subject_data = missing_visits_df[missing_visits_df[subject_col] == subject]
                    row['missing_visits'] = len(subject_data)
            
            # Extract EDRR issues (queries)
            if edrr_df is not None and not edrr_df.empty:
                subject_col = self._find_subject_column(edrr_df)
                if subject_col:
                    subject_data = edrr_df[edrr_df[subject_col] == subject]
                    if not subject_data.empty and 'Total Open issue Count per subject' in subject_data.columns:
                        row['open_lnr_issues'] = int(subject_data.iloc[0]['Total Open issue Count per subject'])
                        row['open_queries'] += row['open_lnr_issues']
            
            # Extract SAE issues
            if sae_df is not None and not sae_df.empty:
                subject_col = self._find_subject_column(sae_df)
                if subject_col:
                    subject_data = sae_df[sae_df[subject_col] == subject]
                    row['sae_review'] = len(subject_data)
                    row['open_queries'] += len(subject_data)
            
            # Extract coding issues
            if coding_df is not None and not coding_df.empty:
                subject_col = self._find_subject_column(coding_df)
                if subject_col:
                    subject_data = coding_df[coding_df[subject_col] == subject]
                    if not subject_data.empty and 'Coding Status' in subject_data.columns:
                        coded = len(subject_data[subject_data['Coding Status'] == 'Coded Term'])
                        uncoded = len(subject_data[subject_data['Coding Status'] != 'Coded Term'])
                        row['coded_terms'] = coded
                        row['uncoded_terms'] = uncoded
                        row['open_queries'] += uncoded
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Fill missing site_id from other sources if needed
        if df['site_id'].isna().any():
            # Try to get from visit projections
            if missing_visits_df is not None and not missing_visits_df.empty:
                site_col = self._find_site_column(missing_visits_df)
                subject_col = self._find_subject_column(missing_visits_df)
                if site_col and subject_col:
                    for idx, row in df[df['site_id'].isna()].iterrows():
                        subject_data = missing_visits_df[missing_visits_df[subject_col] == row['subject_id']]
                        if not subject_data.empty:
                            df.at[idx, 'site_id'] = subject_data.iloc[0][site_col]
                            if 'Country' in subject_data.columns:
                                df.at[idx, 'country'] = subject_data.iloc[0]['Country']
        
        return df
    
    def discover_studies(self) -> list:
        """Discover all study folders in data directory"""
        studies = []
        for item in self.data_directory.iterdir():
            if item.is_dir() and (item.name.startswith("Study") or item.name.startswith("study")):
                studies.append(item.name)
        
        logger.info(f"Discovered {len(studies)} studies")
        return sorted(studies)
