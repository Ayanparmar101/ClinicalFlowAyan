# Archived Scripts

This directory contains utility and debugging scripts archived during the codebase cleanup on January 31, 2026.

## Directory Structure

### debugging/
One-time debugging scripts used during development (9 files):
- `debug_study6.py` - Study 6 specific debugging
- `inspect_study17_raw.py` - Raw data inspection for Study 17
- `inspect_study17.py` - Study 17 analysis
- `check_all_files.py` - File completeness checker
- `check_columns.py` - Column validation
- `check_completeness_data.py` - Data completeness validation
- `check_raw_values.py` - Raw value inspection
- `check_structure.py` - Structure validation
- `quick_fix_metrics.py` - Metrics quick fix utility

### utilities/
General utility scripts (4 files):
- `analyze_structure.py` - Codebase structure analyzer
- `list_available_models.py` - List available AI models
- `list_models.py` - Model listing utility
- `rename_study_folders.py` - Batch folder renaming

## Active Scripts

The following scripts remain active in the parent directory:
- `verify_upload_feature.py` - Upload feature verification
- `wait_for_load.py` - Loading wait utility
- `README.md` - Scripts documentation

**Reason for archival**: These were one-time use scripts for debugging specific issues or performing data migration tasks. They are no longer needed for regular development.

## Restoration

If needed, restore any script:
```powershell
Move-Item scripts\archive\debugging\script_name.py scripts\script_name.py
```
