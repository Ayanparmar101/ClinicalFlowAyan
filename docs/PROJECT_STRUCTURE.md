# Project Structure

## Root Directory
```
NestTry/
├── .env                    # Environment variables (Gemini API key)
├── .env.example            # Example environment configuration
├── .gitignore              # Git ignore rules
├── LICENSE                 # Project license
├── README.md               # Main project documentation
├── requirements.txt        # Python dependencies
├── src/                    # Main application code
├── clinical-ops-rt/        # Clinical operations package
├── data/                   # Study data files
├── output/                 # Generated reports
├── tests/                  # Test suite
├── scripts/                # Utility scripts
├── docs/                   # Documentation
└── logs/                   # Application logs
```

## Source Code Structure (`src/`)

The main application package containing the core platform functionality.

```
src/
├── main.py                 # CLI entry point
├── config.py               # Configuration management
├── ingestion/              # Data loading and validation
│   ├── data_loader.py      # Main data loader
│   └── multi_file_loader.py # Multi-file processing
├── harmonization/          # Data normalization
│   └── canonical_model.py  # Canonical data model
├── metrics/                # KPI calculations
│   ├── metrics_engine.py   # Main metrics engine
│   └── dqi_calculator.py   # Data Quality Index
├── intelligence/           # Risk detection
│   └── risk_detection.py   # Risk analysis
├── ai/                     # AI capabilities
│   ├── generative_ai.py    # Generative AI integration
│   └── agentic_ai.py       # Agentic AI agents
└── dashboard/              # Web UI
    └── app.py              # Streamlit dashboard
```

## Clinical Operations Package (`clinical-ops-rt/`)

Advanced clinical trial operations package with real-time state management.

```
clinical-ops-rt/
├── README.md
├── ingestion/              # Advanced data loaders
│   ├── visit_projection.py # Visit tracking
│   ├── sae_dashboard.py    # Safety events
│   ├── coding_reports.py   # Medical coding
│   ├── missing_pages.py    # Missing data
│   └── inactivated_forms.py # Form inactivations
├── model/                  # State management
│   ├── state.py            # Subject state (SubjectState class)
│   ├── subject_factory.py  # Subject builder
│   ├── site_state.py       # Site state (SiteState class)
│   ├── site_factory.py     # Site builder
│   └── state_pipeline.py   # State pipeline
├── metrics/                # Risk metrics
│   ├── dqi.py              # Data Quality Index
│   ├── visit_risk.py       # Visit risks
│   ├── sae_risk.py         # Safety risks
│   ├── coding_risk.py      # Coding risks
│   ├── page_risk.py        # Missing page risks
│   └── inactivation_risk.py # Inactivation risks
├── ai/                     # AI algorithms
│   ├── prioritizer.py      # Risk prioritization
│   ├── explainer.py        # AI explainability
│   ├── narrative.py        # Natural language
│   └── study_brief.py      # Study summaries
├── events/                 # Event system
│   └── bus.py              # Event bus
├── events/                 # Event system
│   └── bus.py              # Event bus
└── api/                    # API layer
    └── main.py             # FastAPI API entry point (221 lines)
```

**Note:** Main dashboard is located at `src/dashboard/app.py` (2059 lines, fully implemented).

## Data Directory (`data/`)

Study data organized by study folders:
- Study folders follow naming pattern: `Study N_CPID_Input Files - Anonymization/`
- Each study folder contains Excel files for various data types
- `problem_statement_1/` - Data for problem statement 1

## Tests Directory (`tests/`)

Comprehensive test suite covering all components:
- Component tests (ingestion, metrics, intelligence, AI)
- Integration tests (pipeline, dashboard)
- Study-specific tests
- See `tests/README.md` for details

## Scripts Directory (`scripts/`)

Utility and debugging scripts:
- Data analysis scripts (`analyze_structure.py`, `check_*.py`)
- Debugging scripts (`debug_*.py`, `inspect_*.py`)
- Utility scripts (`list_*.py`, `verify_*.py`)
- See `scripts/README.md` for details

## Documentation Directory (`docs/`)

Complete project documentation:
- `ARCHITECTURE.md` - System architecture
- `USER_GUIDE.md` - User guide
- `DEMO_SCRIPT.md` - Demo instructions
- `QUICKSTART.md` - Quick start guide
- `COMPREHENSIVE_VALIDATION_REPORT.md` - Validation report
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `EXECUTIVE_SUMMARY.md` - Executive summary
- `GEMINI_SETUP.md` - Gemini AI setup
- `GEMINI_API_FIX_GUIDE.md` - API troubleshooting
- `verify_cra_dashboard.md` - CRA dashboard verification
- `CLINICAL_TRIAL_INTELLIGENCE_PLATFORM_DOCUMENTATION.md` - Complete platform docs
- `references/` - Requirements and specifications
- `deprecated/` - Archived documentation

## Output Directory (`output/`)

Generated reports and exports from the system.

## Logs Directory (`logs/`)

Application logs with rotation (500 MB, 10 days retention).

## Important Files

### Configuration
- `.env` - Contains `GEMINI_API_KEY` for AI integration
- `.env.example` - Template for environment variables

### Dependencies
- `requirements.txt` - Python package dependencies

### Version Control
- `.gitignore` - Excludes logs, cache, virtual env, data files

## Running the Application

### Dashboard
```bash
streamlit run src/dashboard/app.py
```

### CLI
```bash
python src/main.py
```

### Tests
```bash
pytest tests/
```

### Scripts
```bash
python scripts/script_name.py
```
