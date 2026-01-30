# Tests Directory

Comprehensive test suite for the Clinical Trial Intelligence Platform.

## Test Structure

### Core Component Tests
- `test_ingestion_validation.py` - Data ingestion validation
- `test_metrics_calc.py` - Metric calculation tests
- `test_installation.py` - Installation verification

### Dashboard Tests
- `test_cra_dashboard.py` - CRA dashboard functionality
- `test_dashboard_imports.py` - Dashboard import validation

### Pipeline Tests
- `test_complete_pipeline.py` - End-to-end pipeline testing
- `direct_pipeline_test.py` - Direct pipeline execution
- `simple_test.py` - Simple smoke tests

### Data Loading Tests
- `test_new_loader.py` - New data loader tests
- `test_new_loading.py` - Loading mechanism tests
- `test_direct_file.py` - Direct file loading
- `test_column_mapping.py` - Column mapping validation
- `test_parser_debug.py` - Parser debugging

### AI Integration Tests
- `test_gemini.py` - Gemini AI integration
- `test_gemini_api.py` - Gemini API tests
- `test_gemini_rest.py` - Gemini REST API tests

### Study-Specific Tests
- `test_study6_metrics.py` - Study 6 metrics validation
- `test_multiple_studies.py` - Multi-study processing

### Clinical Operations Tests (from clinical-ops-rt)
- `test_coding_risk.py` - Coding risk assessment
- `test_full_state.py` - Full state management
- `test_pages_and_inactivation.py` - Page and inactivation tests
- `test_read_cpid.py` - CPID reading tests
- `test_sae_dashboard.py` - SAE dashboard tests
- `test_site_state.py` - Site state management
- `test_subject_state.py` - Subject state management
- `test_visit_projection.py` - Visit projection tests

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run specific test file
```bash
pytest tests/test_name.py
```

### Run with coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run with verbose output
```bash
pytest tests/ -v
```
