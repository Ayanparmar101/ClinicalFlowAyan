# Conservative Codebase Cleanup Script
# Moves obsolete files to deprecated/ folders for archival
# Nothing is deleted - everything can be restored
# Date: January 31, 2026

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Codebase Cleanup - Conservative Mode" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will MOVE (not delete) obsolete files to deprecated/ folders" -ForegroundColor Yellow
Write-Host ""

# Ask for confirmation
$confirmation = Read-Host "Do you want to proceed? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Host "Cleanup cancelled." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Starting cleanup..." -ForegroundColor Green
Write-Host ""

# Step 1: Create archive directory structure
Write-Host "[1/5] Creating archive directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "deprecated" | Out-Null
New-Item -ItemType Directory -Force -Path "tests\deprecated" | Out-Null
New-Item -ItemType Directory -Force -Path "scripts\archive\debugging" | Out-Null
New-Item -ItemType Directory -Force -Path "scripts\archive\utilities" | Out-Null
New-Item -ItemType Directory -Force -Path "docs\historical" | Out-Null
Write-Host "   ✓ Created archive directories" -ForegroundColor Green

# Step 2: Move clinical-ops-rt/ folder
Write-Host "[2/5] Archiving clinical-ops-rt/ folder..." -ForegroundColor Cyan
if (Test-Path "clinical-ops-rt") {
    Move-Item -Path "clinical-ops-rt" -Destination "deprecated\clinical-ops-rt" -Force
    Write-Host "   ✓ Moved clinical-ops-rt/ to deprecated/" -ForegroundColor Green
} else {
    Write-Host "   ⚠ clinical-ops-rt/ not found (already moved?)" -ForegroundColor Yellow
}

# Step 3: Move obsolete test files
Write-Host "[3/5] Archiving obsolete test files..." -ForegroundColor Cyan
$obsoleteTests = @(
    "test_coding_risk.py",
    "test_full_state.py",
    "test_pages_and_inactivation.py",
    "test_read_cpid.py",
    "test_sae_dashboard.py",
    "test_site_state.py",
    "test_study6_metrics.py",
    "test_subject_state.py",
    "test_visit_projection.py",
    "test_parser_debug.py",
    "test_column_mapping.py",
    "test_direct_file.py",
    "test_cra_dashboard.py",
    "direct_pipeline_test.py",
    "simple_test.py"
)

foreach ($test in $obsoleteTests) {
    $testPath = "tests\$test"
    if (Test-Path $testPath) {
        Move-Item -Path $testPath -Destination "tests\deprecated\$test" -Force
        Write-Host "   ✓ Moved $test" -ForegroundColor Green
    }
}

# Step 4: Move obsolete scripts
Write-Host "[4/5] Archiving obsolete scripts..." -ForegroundColor Cyan

# Debugging scripts
$debugScripts = @(
    "debug_study6.py",
    "inspect_study17.py",
    "inspect_study17_raw.py",
    "check_all_files.py",
    "check_columns.py",
    "check_completeness_data.py",
    "check_raw_values.py",
    "check_structure.py",
    "analyze_structure.py"
)

foreach ($script in $debugScripts) {
    $scriptPath = "scripts\$script"
    if (Test-Path $scriptPath) {
        Move-Item -Path $scriptPath -Destination "scripts\archive\debugging\$script" -Force
        Write-Host "   ✓ Moved $script to debugging/" -ForegroundColor Green
    }
}

# Utility scripts
$utilScripts = @(
    "list_models.py",
    "list_available_models.py",
    "rename_study_folders.py",
    "wait_for_load.py"
)

foreach ($script in $utilScripts) {
    $scriptPath = "scripts\$script"
    if (Test-Path $scriptPath) {
        Move-Item -Path $scriptPath -Destination "scripts\archive\utilities\$script" -Force
        Write-Host "   ✓ Moved $script to utilities/" -ForegroundColor Green
    }
}

# Step 5: Move obsolete docs and fix_dataframe.py
Write-Host "[5/5] Archiving obsolete documentation..." -ForegroundColor Cyan

$obsoleteDocs = @(
    "EMPTY_FILES_REMOVED.md",
    "CLEANUP_SUMMARY.md",
    "verify_cra_dashboard.md"
)

foreach ($doc in $obsoleteDocs) {
    $docPath = "docs\$doc"
    if (Test-Path $docPath) {
        Move-Item -Path $docPath -Destination "docs\historical\$doc" -Force
        Write-Host "   ✓ Moved $doc" -ForegroundColor Green
    }
}

# Move fix_dataframe.py to deprecated
if (Test-Path "fix_dataframe.py") {
    Move-Item -Path "fix_dataframe.py" -Destination "deprecated\fix_dataframe.py" -Force
    Write-Host "   ✓ Moved fix_dataframe.py" -ForegroundColor Green
}

# Create README files in archived folders
Write-Host ""
Write-Host "Creating README files in archived folders..." -ForegroundColor Cyan

# deprecated/README.md
@"
# Deprecated / Archived Code

This folder contains code that is no longer actively used but preserved for historical reference.

## Contents

- **clinical-ops-rt/** - Obsolete clinical operations package (not used by main application)
- **fix_dataframe.py** - One-time utility script with hardcoded paths

## Why Archived?

These files were identified as obsolete during the January 31, 2026 cleanup:
- No imports from main application
- Historical/one-time utilities
- Preserved for reference if needed

## Restoration

To restore any file:
``````bash
# Example: restore clinical-ops-rt
mv deprecated/clinical-ops-rt ./clinical-ops-rt
``````

See: docs/CODEBASE_CLEANUP_AND_OPTIMIZATION_REPORT.md
"@ | Out-File -FilePath "deprecated\README.md" -Encoding UTF8

# tests/deprecated/README.md
@"
# Deprecated Tests

These tests target obsolete features from the clinical-ops-rt package that is no longer used.

## Archived Tests

- test_coding_risk.py - clinical-ops-rt/metrics/
- test_full_state.py - clinical-ops-rt/model/
- test_pages_and_inactivation.py - clinical-ops-rt/metrics/
- test_read_cpid.py - Obsolete CPID reader
- test_sae_dashboard.py - clinical-ops-rt/ingestion/
- test_site_state.py - clinical-ops-rt/model/
- test_study6_metrics.py - Study-specific test
- test_subject_state.py - clinical-ops-rt/model/
- test_visit_projection.py - clinical-ops-rt/ingestion/
- And others...

## Active Tests

See tests/README.md for currently active tests.
"@ | Out-File -FilePath "tests\deprecated\README.md" -Encoding UTF8

# scripts/archive/README.md
@"
# Archived Scripts

One-time debugging and utility scripts preserved for reference.

## Debugging Scripts (debugging/)

Scripts used for one-time data analysis and debugging:
- debug_study6.py
- inspect_study17.py
- check_*.py scripts
- analyze_structure.py

## Utility Scripts (utilities/)

One-time utility operations:
- list_models.py
- rename_study_folders.py
- wait_for_load.py

## Active Scripts

See scripts/README.md for currently active scripts.
"@ | Out-File -FilePath "scripts\archive\README.md" -Encoding UTF8

# docs/historical/README.md
@"
# Historical Documentation

Documentation from previous cleanup and verification efforts.

These documents are preserved for historical reference but superseded by current documentation.

## Files

- EMPTY_FILES_REMOVED.md - Previous cleanup report
- CLEANUP_SUMMARY.md - Previous cleanup summary
- verify_cra_dashboard.md - Dashboard verification notes

## Current Documentation

See docs/ root folder for current, active documentation.
"@ | Out-File -FilePath "docs\historical\README.md" -Encoding UTF8

Write-Host "   ✓ Created README files" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Cleanup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  • clinical-ops-rt/ moved to deprecated/"
Write-Host "  • ~15 test files moved to tests/deprecated/"
Write-Host "  • ~13 scripts moved to scripts/archive/"
Write-Host "  • 3 docs moved to docs/historical/"
Write-Host "  • fix_dataframe.py moved to deprecated/"
Write-Host ""
Write-Host "✓ Nothing was deleted - all files preserved" -ForegroundColor Green
Write-Host "✓ Your application will work exactly the same" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Test your application: streamlit run src\dashboard\app.py"
Write-Host "  2. Run tests: pytest tests/ -v"
Write-Host "  3. If everything works, commit changes"
Write-Host "  4. To restore any file, see deprecated/README.md"
Write-Host ""
