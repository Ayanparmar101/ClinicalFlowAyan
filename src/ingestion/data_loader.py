"""
Data Ingestion Module
Handles loading and validation of clinical trial data files
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re
from loguru import logger

# Import from config module
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import DATA_PATH, FILE_TYPE_PATTERNS

# Import new multi-file loader
from .multi_file_loader import MultiFileDataLoader


class DataIngestionEngine:
    """
    Main engine for ingesting clinical trial data from Excel files
    Uses multi-file loader to aggregate data from specialized reports
    """
    
    def __init__(self, data_directory: Optional[Path] = None):
        """
        Initialize the data ingestion engine
        
        Args:
            data_directory: Path to the directory containing data files
        """
        self.data_directory = data_directory or DATA_PATH
        self.multi_file_loader = MultiFileDataLoader(self.data_directory)
        self.ingestion_metadata = {
            "timestamp": datetime.now(),
            "files_processed": [],
            "errors": []
        }
        logger.info(f"Data Ingestion Engine initialized with directory: {self.data_directory}")
    
    def discover_studies(self) -> List[str]:
        """
        Discover all study folders in the data directory
        
        Returns:
            List of study folder names
        """
        return self.multi_file_loader.discover_studies()
    
    def load_study_data(self, study_name: str) -> Optional[pd.DataFrame]:
        """
        Load all data for a specific study using multi-file loader
        
        Args:
            study_name: Name of the study folder
            
        Returns:
            DataFrame with consolidated subject-level metrics
        """
        logger.info(f"Loading study data: {study_name}")
        
        # Use multi-file loader to get consolidated data
        df = self.multi_file_loader.load_study_data(study_name)
        
        if df is not None and not df.empty:
            logger.info(f"Successfully loaded {study_name}: {len(df)} subjects")
            self.ingestion_metadata["files_processed"].append(study_name)
            return df
        else:
            logger.warning(f"No data loaded for {study_name}")
            return None
    
    def load_excel_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        Load an Excel file with error handling and proper header detection
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            DataFrame if successful, None otherwise
        """
        try:
            # First, read raw to detect structure
            file_name_lower = file_path.name.lower()
            
            # EDC Metrics files have complex multi-level headers
            if "edc" in file_name_lower or "cpid" in file_name_lower:
                df = self._load_edc_metrics_file(file_path)
            elif "missing" in file_name_lower and "page" in file_name_lower:
                df = self._load_missing_pages_file(file_path)
            elif "sae" in file_name_lower or "esae" in file_name_lower:
                df = self._load_sae_file(file_path)
            else:
                # Standard load for other file types
                if file_path.suffix.lower() == '.xlsx':
                    df = pd.read_excel(file_path, engine='openpyxl')
                else:
                    df = pd.read_excel(file_path, engine='xlrd')
            
            if df is not None and not df.empty:
                logger.info(f"Successfully loaded: {file_path.name} ({len(df)} rows)")
                self.ingestion_metadata["files_processed"].append(str(file_path))
                return df
            else:
                logger.warning(f"Empty dataframe from {file_path.name}")
                return None
        
        except Exception as e:
            error_msg = f"Error loading {file_path.name}: {str(e)}"
            logger.error(error_msg)
            self.ingestion_metadata["errors"].append(error_msg)
            return None
    
    def _load_edc_metrics_file(self, file_path: Path) -> pd.DataFrame:
        """
        Load EDC Metrics file with complex multi-level header structure
        Structure: Row 0-2 are headers, Row 3+ is data
        """
        try:
            # Read raw data to understand structure
            raw_df = pd.read_excel(file_path, header=None, engine='openpyxl')
            
            if raw_df.empty or len(raw_df) < 4:
                return pd.DataFrame()
            
            # Extract header rows
            header_row1 = raw_df.iloc[0].fillna('')
            header_row2 = raw_df.iloc[1].fillna('')
            header_row3 = raw_df.iloc[2].fillna('')
            
            # Build proper column names by combining headers
            columns = []
            for i in range(len(header_row1)):
                h1 = str(header_row1.iloc[i]).strip()
                h2 = str(header_row2.iloc[i]).strip()
                h3 = str(header_row3.iloc[i]).strip()
                
                # Combine non-empty parts
                parts = [p for p in [h1, h2, h3] if p and p != 'nan' and p != '']
                
                if parts:
                    col_name = ' - '.join(parts) if len(parts) > 1 else parts[0]
                else:
                    col_name = f'Column_{i}'
                
                columns.append(col_name)
            
            # Extract data (skip first 3 header rows and any empty rows after)
            data_df = raw_df.iloc[3:].copy()
            data_df.columns = columns
            
            # Remove rows where key identifiers are missing
            data_df = data_df.dropna(subset=[col for col in data_df.columns if 'Subject' in col or 'Site' in col], how='all')
            
            # Clean up: remove completely empty rows
            data_df = data_df.replace('', np.nan)
            data_df = data_df.dropna(how='all')
            
            # Convert numeric columns
            for col in data_df.columns:
                if any(keyword in col for keyword in ['Missing', '#', 'Open', 'Closed', 'Total', 'Count']):
                    data_df[col] = pd.to_numeric(data_df[col], errors='coerce').fillna(0)
            
            logger.debug(f"Parsed EDC file with {len(data_df)} rows and columns: {list(data_df.columns[:10])}")
            return data_df
            
        except Exception as e:
            logger.error(f"Error parsing EDC metrics file {file_path.name}: {e}")
            return pd.DataFrame()
    
    def _load_missing_pages_file(self, file_path: Path) -> pd.DataFrame:
        """Load missing pages report file"""
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            # Clean up column names
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            logger.error(f"Error parsing missing pages file {file_path.name}: {e}")
            return pd.DataFrame()
    
    def _load_sae_file(self, file_path: Path) -> pd.DataFrame:
        """Load SAE dashboard file"""
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            # Clean up column names
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            logger.error(f"Error parsing SAE file {file_path.name}: {e}")
            return pd.DataFrame()
    
    def classify_file_type(self, file_name: str) -> Optional[str]:
        """
        Classify file based on its name pattern
        
        Args:
            file_name: Name of the file
            
        Returns:
            File type key or None if unclassified
        """
        file_name_lower = file_name.lower()
        
        # Classification rules based on hackathon dataset patterns
        if "edc_metrics" in file_name_lower or "cpid" in file_name_lower:
            return "edc_metrics"
        elif "missing_pages" in file_name_lower or "missing pages" in file_name_lower:
            return "missing_pages"
        elif "sae" in file_name_lower and "dashboard" in file_name_lower:
            return "sae_dashboard"
        elif "coding" in file_name_lower:
            if "meddra" in file_name_lower:
                return "coding_meddra"
            elif "who" in file_name_lower:
                return "coding_whodd"
            else:
                return "coding_report"
        elif "lab" in file_name_lower and ("missing" in file_name_lower or "range" in file_name_lower):
            return "lab_report"
        elif "visit" in file_name_lower and "projection" in file_name_lower:
            return "visit_projection"
        elif "inactivated" in file_name_lower:
            return "inactivated_forms"
        elif "edrr" in file_name_lower:
            return "edrr"
        else:
            return None
    
    def ingest_study_data(self, study_name: str) -> Dict[str, pd.DataFrame]:
        """
        Ingest all data files for a specific study
        
        Args:
            study_name: Name of the study folder
            
        Returns:
            Dictionary mapping file types to DataFrames
        """
        study_path = self.data_directory / study_name
        study_data = {}
        
        if not study_path.exists():
            logger.warning(f"Study path does not exist: {study_path}")
            return study_data
        
        logger.info(f"Ingesting data for study: {study_name}")
        
        # Find all Excel files in the study directory
        excel_files = list(study_path.glob("*.xlsx")) + list(study_path.glob("*.xls"))
        
        for file_path in excel_files:
            file_type = self.classify_file_type(file_path.name)
            
            if file_type:
                df = self.load_excel_file(file_path)
                if df is not None:
                    # Add metadata columns
                    df['_study'] = study_name
                    df['_file_source'] = file_path.name
                    df['_ingestion_timestamp'] = self.ingestion_metadata["timestamp"]
                    
                    study_data[file_type] = df
                    logger.info(f"Classified {file_path.name} as {file_type}")
            else:
                logger.warning(f"Could not classify file: {file_path.name}")
        
        return study_data
    
    def ingest_all_studies(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Ingest data from all discovered studies
        
        Returns:
            Nested dictionary: study_name -> file_type -> DataFrame
        """
        all_data = {}
        studies = self.discover_studies()
        
        logger.info(f"Starting ingestion of {len(studies)} studies")
        
        for study in studies:
            study_data = self.ingest_study_data(study)
            if study_data:
                all_data[study] = study_data
        
        logger.info(f"Ingestion complete. Processed {len(all_data)} studies")
        return all_data
    
    def get_ingestion_summary(self) -> Dict:
        """
        Get a summary of the ingestion process
        
        Returns:
            Dictionary containing ingestion metadata
        """
        return {
            "timestamp": self.ingestion_metadata["timestamp"],
            "files_processed_count": len(self.ingestion_metadata["files_processed"]),
            "files_processed": self.ingestion_metadata["files_processed"],
            "errors_count": len(self.ingestion_metadata["errors"]),
            "errors": self.ingestion_metadata["errors"]
        }


def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate that a DataFrame contains required columns
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        Tuple of (is_valid, missing_columns)
    """
    if df is None or df.empty:
        return False, required_columns
    
    df_columns = [col.lower().strip() for col in df.columns]
    missing = []
    
    for req_col in required_columns:
        req_col_variants = [req_col.lower().strip(), req_col.lower().replace(" ", ""), req_col.lower().replace("_", "")]
        if not any(variant in df_columns for variant in req_col_variants):
            missing.append(req_col)
    
    return len(missing) == 0, missing
