# Deprecated Tests

This directory contains test files that were archived during the codebase cleanup on January 31, 2026.

## Archived Tests

### Clinical Operations Tests (15 files)
Tests targeting the `clinical-ops-rt/` package which has been archived:
- `test_clinical_api.py`
- `test_clinical_events.py`
- `test_clinical_ingestion.py`
- `test_clinical_metrics.py`
- `test_clinical_model.py`
- `test_events.py`
- `test_llm_api.py`
- `test_metrics_service.py`
- `test_model_integration.py`
- `test_realtime_processor.py`
- `test_study_processor.py`
- `conftest_clinical.py`

### Duplicate API Tests (3 files)
- `test_gemini_api_duplicate1.py`
- `test_gemini_api_duplicate2.py`
- `test_gemini_integration.py`

**Reason for archival**: These tests target code that no longer exists in the active codebase (clinical-ops-rt package) or are duplicates of existing tests.

## Active Tests

The following tests remain active in the parent directory and cover the current application:
- `test_gemini_api.py` - Gemini API integration tests
- `test_harmonization.py` - Data harmonization tests
- `test_ingestion.py` - Data ingestion tests
- `test_intelligence.py` - Intelligence services tests
- `test_metrics.py` - Metrics calculation tests
- `test_config.py` - Configuration tests
- `conftest.py` - Main pytest configuration

## Restoration

If needed, restore any test file:
```powershell
Move-Item tests\deprecated\test_name.py tests\test_name.py
```
