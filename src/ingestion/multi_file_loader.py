"""
Multi-File Data Loader - Loads clinical trial metrics from multiple specialized Excel files
Implements robust subject-level aggregation pipeline for clean rate calculation
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
    
    Pipeline Steps:
    1. Load master subject list (denominator) from EDC Metrics
    2. Aggregate missing visits from Visit Projection
    3. Aggregate missing pages from Missing Pages (excluding inactivated forms)
    4. Aggregate open queries from EDRR and other sources
    5. Aggregate pending SDV from SDV metrics
    6. Aggregate open safety issues from SAE Dashboard
    7. Join all metrics at subject level
    8. Calculate is_clean_patient flag
    9. Calculate clean rate
    """
    
    def __init__(self, data_directory: Path):
        """Initialize with data directory path"""
        self.data_directory = Path(data_directory)
        logger.info(f"MultiFileDataLoader initialized with directory: {data_directory}")
    
    def load_study_data(self, study_name: str) -> Optional[pd.DataFrame]:
        """
        Load all data files for a study and consolidate at subject level
        using robust aggregation pipeline
        
        Args:
            study_name: Name of the study folder
            
        Returns:
            DataFrame with consolidated subject-level metrics including clean_rate
        """
        study_path = self.data_directory / study_name
        
        if not study_path.exists():
            logger.error(f"Study path does not exist: {study_path}")
            return None
        
        logger.info(f"Loading data for {study_name} using robust pipeline")
        
        # Step 1: Load master subject list (the denominator)
        subject_master = self._load_subject_master(study_path, study_name)
        if subject_master is None or subject_master.empty:
            logger.warning(f"No master subject list found for {study_name}")
            return None
        
        logger.info(f"Step 1 complete: {len(subject_master)} subjects in master list")
        
        # Step 2: Load and aggregate missing visits
        missing_visits_agg = self._aggregate_missing_visits(study_path)
        logger.info(f"Step 2 complete: Missing visits loaded")
        
        # Step 3: Load and aggregate missing pages (excluding inactivated)
        missing_pages_agg = self._aggregate_missing_pages(study_path)
        logger.info(f"Step 3 complete: Missing pages loaded")
        
        # Step 4: Load and aggregate open queries
        open_queries_agg = self._aggregate_open_queries(study_path)
        logger.info(f"Step 4 complete: Open queries loaded")
        
        # Step 5: Load and aggregate pending SDV
        pending_sdv_agg = self._aggregate_pending_sdv(study_path)
        logger.info(f"Step 5 complete: Pending SDV loaded")
        
        # Step 6: Load and aggregate open safety issues
        safety_issues_agg = self._aggregate_safety_issues(study_path)
        logger.info(f"Step 6 complete: Safety issues loaded")
        
        # Step 7: Join all metrics to subject_master (left join)
        consolidated = self._join_all_metrics(
            subject_master,
            missing_visits_agg,
            missing_pages_agg,
            open_queries_agg,
            pending_sdv_agg,
            safety_issues_agg
        )
        logger.info(f"Step 7 complete: All metrics joined at subject level")
        
        # Step 8: Calculate is_clean_patient flag
        consolidated = self._calculate_clean_patient_flag(consolidated)
        logger.info(f"Step 8 complete: Clean patient flags calculated")
        
        # Step 9: Clean rate is calculated at analysis time
        clean_count = consolidated['is_clean_patient'].sum()
        total_count = len(consolidated)
        clean_rate = (clean_count / total_count * 100) if total_count > 0 else 0
        logger.info(f"Step 9 complete: Clean rate = {clean_rate:.1f}% ({clean_count}/{total_count} subjects)")
        
        return consolidated
    
    def _load_subject_master(self, study_path: Path, study_name: str) -> Optional[pd.DataFrame]:
        """
        Step 1: Load master subject list from EDC Metrics file
        This is the denominator - all subjects entered into EDC
        
        Returns:
            DataFrame with columns: subject_id, site_id, country, region, subject_status
        """
        try:
            # Look for EDC Metrics file
            edc_files = list(study_path.glob('*EDC*Metrics*.xlsx'))
            if not edc_files:
                logger.warning(f"No EDC Metrics file found for {study_name}")
                # Fallback: gather subjects from all available files
                return self._fallback_subject_master(study_path, study_name)
            
            df = pd.read_excel(edc_files[0])
            logger.debug(f"Loaded EDC Metrics: {len(df)} rows, columns: {list(df.columns[:10])}")
            
            # Find subject column
            subject_col = self._find_subject_column(df)
            if not subject_col:
                logger.error("Subject ID column not found in EDC Metrics")
                return None
            
            # Extract subject-level master data
            master = df[[subject_col]].copy()
            master.columns = ['subject_id']
            
            # Add site_id if available
            site_col = self._find_site_column(df)
            if site_col:
                master['site_id'] = df[site_col]
            else:
                master['site_id'] = None
            
            # Add country if available
            country_cols = [c for c in df.columns if 'country' in c.lower()]
            if country_cols:
                master['country'] = df[country_cols[0]]
            else:
                master['country'] = None
            
            # Add region if available
            region_cols = [c for c in df.columns if 'region' in c.lower()]
            if region_cols:
                master['region'] = df[region_cols[0]]
            else:
                master['region'] = None
            
            # Add subject status if available
            status_cols = [c for c in df.columns if 'status' in c.lower() and 'subject' in c.lower()]
            if status_cols:
                master['subject_status'] = df[status_cols[0]]
            else:
                master['subject_status'] = 'Unknown'
            
            # Deduplicate by subject_id
            master = master.drop_duplicates(subset=['subject_id']).reset_index(drop=True)
            master['study_id'] = study_name
            
            logger.info(f"Master subject list: {len(master)} unique subjects")
            return master
            
        except Exception as e:
            logger.error(f"Error loading subject master: {e}")
            return None
    
    def _fallback_subject_master(self, study_path: Path, study_name: str) -> Optional[pd.DataFrame]:
        """Fallback: gather unique subjects from all available files"""
        all_subjects = set()
        all_data = []
        
        # Try each file type
        for pattern in ['*Missing_Pages*.xlsx', '*Visit*Projection*.xlsx', '*EDRR*.xlsx', '*SAE*.xlsx']:
            files = list(study_path.glob(pattern))
            if files:
                try:
                    df = pd.read_excel(files[0])
                    subject_col = self._find_subject_column(df)
                    if subject_col:
                        subjects = df[subject_col].unique()
                        all_subjects.update(subjects)
                        all_data.append(df)
                except:
                    continue
        
        if not all_subjects:
            return None
        
        master = pd.DataFrame({
            'subject_id': sorted(list(all_subjects)),
            'site_id': None,
            'country': None,
            'region': None,
            'subject_status': 'Unknown',
            'study_id': study_name
        })
        
        logger.info(f"Fallback master list: {len(master)} subjects from multiple files")
        return master
    
    def _aggregate_missing_visits(self, study_path: Path) -> pd.DataFrame:
        """
        Step 2: Aggregate missing visits per subject from Visit Projection Tracker
        
        Returns:
            DataFrame with columns: subject_id, missing_visits
        """
    
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
    
    def _aggregate_missing_visits(self, study_path: Path) -> pd.DataFrame:
        """
        Step 2: Aggregate missing visits per subject from Visit Projection Tracker
        
        Returns:
            DataFrame with columns: subject_id, missing_visits
        """
        try:
            files = list(study_path.glob('*Visit*Projection*.xlsx'))
            if not files:
                logger.debug("No visit projection file found")
                return pd.DataFrame(columns=['subject_id', 'missing_visits'])
            
            df = pd.read_excel(files[0])
            
            # Handle header rows
            if 'Unnamed' in str(df.columns[0]) or (len(df) > 0 and 'Restricted' in str(df.iloc[0, 0])):
                df = pd.read_excel(files[0], skiprows=2)
            
            subject_col = self._find_subject_column(df)
            if not subject_col:
                logger.debug("No subject column in visit projection")
                return pd.DataFrame(columns=['subject_id', 'missing_visits'])
            
            # Count rows per subject (each row is a missing visit)
            agg = df.groupby(subject_col).size().reset_index()
            agg.columns = ['subject_id', 'missing_visits']
            
            logger.debug(f"Aggregated missing visits: {len(agg)} subjects")
            return agg
            
        except Exception as e:
            logger.error(f"Error aggregating missing visits: {e}")
            return pd.DataFrame(columns=['subject_id', 'missing_visits'])
    
    def _aggregate_missing_pages(self, study_path: Path) -> pd.DataFrame:
        """
        Step 3: Aggregate missing pages per subject (excluding inactivated forms AND future visits)
        
        CRITICAL: For clean rate, only count missing pages for DUE visits, not future visits.
        You cannot penalize data that is not yet expected to exist.
        
        Returns:
            DataFrame with columns: subject_id, missing_pages
        """
        try:
            # Load missing pages
            files = list(study_path.glob('*Missing_Pages*.xlsx'))
            if not files:
                logger.debug("No missing pages file found")
                return pd.DataFrame(columns=['subject_id', 'missing_pages'])
            
            df = pd.read_excel(files[0])
            subject_col = self._find_subject_column(df)
            
            if not subject_col:
                logger.debug("No subject column in missing pages")
                return pd.DataFrame(columns=['subject_id', 'missing_pages'])
            
            # Load inactivated forms to exclude them
            inactivated_forms = set()
            inactivated_files = list(study_path.glob('*Inactivated*.xlsx'))
            if inactivated_files:
                try:
                    inact_df = pd.read_excel(inactivated_files[0])
                    form_cols = [c for c in inact_df.columns if 'form' in c.lower() or 'folder' in c.lower()]
                    if form_cols:
                        inactivated_forms = set(inact_df[form_cols[0]].dropna().unique())
                        logger.debug(f"Found {len(inactivated_forms)} inactivated forms to exclude")
                except:
                    pass
            
            # Filter out inactivated forms
            form_cols = [c for c in df.columns if 'form' in c.lower() or 'folder' in c.lower()]
            if form_cols and inactivated_forms:
                initial_count = len(df)
                df = df[~df[form_cols[0]].isin(inactivated_forms)]
                logger.debug(f"Excluded inactivated forms: {initial_count} → {len(df)} rows")
            
            # CRITICAL FIX: Filter to DUE VISITS ONLY
            # Load Visit Projection to identify which visits are actually due
            due_visits = self._get_due_visits(study_path)
            
            if not due_visits.empty:
                # Filter missing pages to only include due visits
                visit_cols = [c for c in df.columns if 'visit' in c.lower() and 'missing' not in c.lower()]
                if visit_cols and subject_col in df.columns:
                    # Create a key to match with due_visits
                    df['_key'] = df[subject_col].astype(str) + '_' + df[visit_cols[0]].astype(str)
                    due_visits['_key'] = due_visits['subject_id'].astype(str) + '_' + due_visits['visit_name'].astype(str)
                    
                    initial_count = len(df)
                    df = df[df['_key'].isin(due_visits['_key'])]
                    
                    if len(df) == 0:
                        logger.warning(f"Due visits filter removed ALL missing pages ({initial_count} → 0). This likely means visit names don't match. Falling back to count all missing pages.")
                        # Reload without filter
                        df = pd.read_excel(files[0])
                        if form_cols and inactivated_forms:
                            df = df[~df[form_cols[0]].isin(inactivated_forms)]
                    else:
                        logger.info(f"Filtered to DUE visits only: {initial_count} → {len(df)} missing pages (removed {initial_count - len(df)} future/not-due pages)")
                        df = df.drop(columns=['_key'])
                else:
                    logger.warning("Could not filter by due visits - visit column not found in missing pages")
            else:
                logger.warning("No due visits identified - counting all missing pages (excluding inactivated)")
            
            # Count rows per subject (each row is a missing page for a DUE visit)
            if len(df) == 0:
                logger.info("No missing pages after filtering")
                return pd.DataFrame(columns=['subject_id', 'missing_pages'])
            
            agg = df.groupby(subject_col).size().reset_index()
            agg.columns = ['subject_id', 'missing_pages']
            
            logger.info(f"Aggregated missing pages (DUE visits only): {len(agg)} subjects")
            return agg
            
        except Exception as e:
            logger.error(f"Error aggregating missing pages: {e}")
            return pd.DataFrame(columns=['subject_id', 'missing_pages'])
    
    def _get_due_visits(self, study_path: Path) -> pd.DataFrame:
        """
        Identify which visits are DUE (expected and should have data)
        
        Logic:
        - Visit is expected/scheduled in Visit Projection Tracker
        - Visit status is NOT "Future", "Cancelled", "Not Required"
        - OR visit sequence <= (latest completed visit + 1)
        
        Returns:
            DataFrame with columns: subject_id, visit_name, is_due
        """
        try:
            files = list(study_path.glob('*Visit*Projection*.xlsx'))
            if not files:
                logger.debug("No visit projection file - cannot determine due visits")
                return pd.DataFrame(columns=['subject_id', 'visit_name', 'is_due'])
            
            df = pd.read_excel(files[0])
            
            # Handle header rows
            if 'Unnamed' in str(df.columns[0]) or (len(df) > 0 and 'Restricted' in str(df.iloc[0, 0])):
                df = pd.read_excel(files[0], skiprows=2)
            
            subject_col = self._find_subject_column(df)
            if not subject_col:
                return pd.DataFrame(columns=['subject_id', 'visit_name', 'is_due'])
            
            # Find visit name column
            visit_cols = [c for c in df.columns if 'visit' in c.lower() and 'name' in c.lower()]
            if not visit_cols:
                visit_cols = [c for c in df.columns if 'visit' in c.lower() and 'id' not in c.lower()]
            
            if not visit_cols:
                logger.warning("No visit name column found in Visit Projection")
                return pd.DataFrame(columns=['subject_id', 'visit_name', 'is_due'])
            
            visit_col = visit_cols[0]
            
            # Find status column
            status_cols = [c for c in df.columns if 'status' in c.lower() or 'state' in c.lower()]
            
            # Build due visits list
            due_df = df[[subject_col, visit_col]].copy()
            due_df.columns = ['subject_id', 'visit_name']
            
            # Filter out future/cancelled visits if status column exists
            if status_cols:
                status_col = status_cols[0]
                future_statuses = ['future', 'not scheduled', 'cancelled', 'not required', 'skipped']
                mask = ~df[status_col].astype(str).str.lower().isin(future_statuses)
                due_df = due_df[mask]
                logger.debug(f"Filtered by visit status: {len(df)} → {len(due_df)} due visits")
            
            # Alternative: Use sequence logic (latest completed + 1)
            # If a subject has completed Visit 3, then Visits 1, 2, 3, and 4 are "due"
            # This is a fallback when status is unreliable
            
            due_df['is_due'] = True
            logger.info(f"Identified {len(due_df)} due visit records across all subjects")
            return due_df
            
        except Exception as e:
            logger.error(f"Error determining due visits: {e}")
            return pd.DataFrame(columns=['subject_id', 'visit_name', 'is_due'])
    
    def _aggregate_open_queries(self, study_path: Path) -> pd.DataFrame:
        """
        Step 4: Aggregate open queries per subject from EDRR and other query sources
        
        Returns:
            DataFrame with columns: subject_id, open_queries
        """
        all_queries = []
        
        try:
            # Load EDRR issues
            edrr_files = list(study_path.glob('*EDRR*.xlsx'))
            if edrr_files:
                df = pd.read_excel(edrr_files[0])
                subject_col = self._find_subject_column(df)
                
                if subject_col:
                    # Check if there's a count column
                    count_cols = [c for c in df.columns if 'open' in c.lower() and 'count' in c.lower()]
                    if count_cols:
                        # Use the count directly
                        agg = df.groupby(subject_col)[count_cols[0]].first().reset_index()
                        agg.columns = ['subject_id', 'open_queries']
                        agg['open_queries'] = pd.to_numeric(agg['open_queries'], errors='coerce').fillna(0)
                        all_queries.append(agg)
                    else:
                        # Count rows (each row is an open issue)
                        agg = df.groupby(subject_col).size().reset_index()
                        agg.columns = ['subject_id', 'open_queries']
                        all_queries.append(agg)
            
            # Load SAE issues (each is an open query for review)
            sae_files = list(study_path.glob('*SAE*.xlsx'))
            if sae_files:
                df = pd.read_excel(sae_files[0])
                subject_col = self._find_subject_column(df)
                
                if subject_col:
                    agg = df.groupby(subject_col).size().reset_index()
                    agg.columns = ['subject_id', 'sae_queries']
                    all_queries.append(agg)
            
            # Load coding issues (uncoded = open queries)
            coding_files = list(study_path.glob('*MedDRA*.xlsx')) + list(study_path.glob('*WHODD*.xlsx'))
            if coding_files:
                for file in coding_files:
                    df = pd.read_excel(file)
                    subject_col = self._find_subject_column(df)
                    
                    if subject_col and 'Coding Status' in df.columns:
                        # Only count uncoded items
                        uncoded = df[df['Coding Status'] != 'Coded Term']
                        if not uncoded.empty:
                            agg = uncoded.groupby(subject_col).size().reset_index()
                            agg.columns = ['subject_id', 'coding_queries']
                            all_queries.append(agg)
            
            # Combine all query sources
            if not all_queries:
                return pd.DataFrame(columns=['subject_id', 'open_queries'])
            
            # Merge all query sources
            combined = all_queries[0]
            for agg in all_queries[1:]:
                combined = combined.merge(agg, on='subject_id', how='outer')
            
            # Sum all query columns
            query_cols = [c for c in combined.columns if c != 'subject_id']
            combined = combined.fillna(0)
            combined['open_queries'] = combined[query_cols].sum(axis=1)
            
            result = combined[['subject_id', 'open_queries']]
            logger.debug(f"Aggregated open queries: {len(result)} subjects")
            return result
            
        except Exception as e:
            logger.error(f"Error aggregating open queries: {e}")
            return pd.DataFrame(columns=['subject_id', 'open_queries'])
    
    def _aggregate_pending_sdv(self, study_path: Path) -> pd.DataFrame:
        """
        Step 5: Aggregate pending SDV per subject
        
        Returns:
            DataFrame with columns: subject_id, pending_sdv
        """
        try:
            # Look for SDV data in EDC Metrics or separate SDV file
            edc_files = list(study_path.glob('*EDC*Metrics*.xlsx'))
            if edc_files:
                df = pd.read_excel(edc_files[0])
                subject_col = self._find_subject_column(df)
                
                if subject_col:
                    # Look for SDV-related columns
                    sdv_cols = [c for c in df.columns if 'sdv' in c.lower() and ('pending' in c.lower() or 'incomplete' in c.lower() or 'not' in c.lower())]
                    
                    if sdv_cols:
                        agg = df[[subject_col, sdv_cols[0]]].copy()
                        agg.columns = ['subject_id', 'pending_sdv']
                        agg['pending_sdv'] = pd.to_numeric(agg['pending_sdv'], errors='coerce').fillna(0)
                        logger.debug(f"Aggregated pending SDV: {len(agg)} subjects")
                        return agg
            
            # No SDV data found
            logger.debug("No pending SDV data found")
            return pd.DataFrame(columns=['subject_id', 'pending_sdv'])
            
        except Exception as e:
            logger.error(f"Error aggregating pending SDV: {e}")
            return pd.DataFrame(columns=['subject_id', 'pending_sdv'])
    
    def _aggregate_safety_issues(self, study_path: Path) -> pd.DataFrame:
        """
        Step 6: Aggregate open safety issues per subject from SAE Dashboard
        
        Returns:
            DataFrame with columns: subject_id, open_safety_issues
        """
        try:
            sae_files = list(study_path.glob('*SAE*.xlsx'))
            if not sae_files:
                logger.debug("No SAE file found")
                return pd.DataFrame(columns=['subject_id', 'open_safety_issues'])
            
            df = pd.read_excel(sae_files[0])
            subject_col = self._find_subject_column(df)
            
            if not subject_col:
                logger.debug("No subject column in SAE file")
                return pd.DataFrame(columns=['subject_id', 'open_safety_issues'])
            
            # Each SAE row is an open safety issue requiring review
            agg = df.groupby(subject_col).size().reset_index()
            agg.columns = ['subject_id', 'open_safety_issues']
            
            logger.debug(f"Aggregated safety issues: {len(agg)} subjects")
            return agg
            
        except Exception as e:
            logger.error(f"Error aggregating safety issues: {e}")
            return pd.DataFrame(columns=['subject_id', 'open_safety_issues'])
    
    def _join_all_metrics(
        self,
        subject_master: pd.DataFrame,
        missing_visits: pd.DataFrame,
        missing_pages: pd.DataFrame,
        open_queries: pd.DataFrame,
        pending_sdv: pd.DataFrame,
        safety_issues: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Step 7: Left-join all metrics to subject_master
        Fill missing values with 0 (important!)
        
        Returns:
            Consolidated DataFrame with all metrics
        """
        consolidated = subject_master.copy()
        
        # Convert subject_id to string in master to ensure consistent type
        consolidated['subject_id'] = consolidated['subject_id'].astype(str)
        
        # Left join each metric
        for metric_df, metric_name in [
            (missing_visits, 'missing_visits'),
            (missing_pages, 'missing_pages'),
            (open_queries, 'open_queries'),
            (pending_sdv, 'pending_sdv'),
            (safety_issues, 'open_safety_issues')
        ]:
            if not metric_df.empty:
                # Convert subject_id to string in metric DataFrame too
                metric_df = metric_df.copy()
                metric_df['subject_id'] = metric_df['subject_id'].astype(str)
                consolidated = consolidated.merge(metric_df, on='subject_id', how='left')
            else:
                # Add column with zeros if metric not available
                consolidated[metric_name] = 0
        
        # Fill any remaining NaN with 0
        metric_cols = ['missing_visits', 'missing_pages', 'open_queries', 'pending_sdv', 'open_safety_issues']
        for col in metric_cols:
            if col in consolidated.columns:
                consolidated[col] = consolidated[col].fillna(0).astype(int)
            else:
                consolidated[col] = 0
        
        logger.debug(f"Consolidated metrics: {len(consolidated)} subjects with {len(consolidated.columns)} columns")
        return consolidated
    
    def _calculate_clean_patient_flag(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Step 8: Calculate is_clean_patient flag
        
        Clean patient rule:
        - missing_visits == 0
        - missing_pages == 0
        - open_queries == 0
        - pending_sdv == 0
        - open_safety_issues == 0
        
        Returns:
            DataFrame with is_clean_patient column added
        """
        df = df.copy()
        
        df['is_clean_patient'] = (
            (df['missing_visits'] == 0) &
            (df['missing_pages'] == 0) &
            (df['open_queries'] == 0) &
            (df['pending_sdv'] == 0) &
            (df['open_safety_issues'] == 0)
        )
        
        clean_count = df['is_clean_patient'].sum()
        logger.info(f"Clean patient calculation: {clean_count}/{len(df)} subjects are clean")
        
        return df
        logger.info(f"Clean patient calculation: {clean_count}/{len(df)} subjects are clean")
        
        return df
    
    def discover_studies(self) -> list:
        """Discover all study folders in data directory"""
        studies = []
        for item in self.data_directory.iterdir():
            if item.is_dir() and (item.name.startswith("Study") or item.name.startswith("study") or item.name.startswith("STUDY")):
                studies.append(item.name)
        
        logger.info(f"Discovered {len(studies)} studies")
        return sorted(studies)

