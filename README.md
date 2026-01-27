# Clinical Trial Intelligence Platform

## Overview
An integrated insight-driven clinical trial dataflow platform that transforms fragmented operational reports into actionable intelligence using Generative and Agentic AI.

## Features
- **Unified Data Integration**: Harmonizes clinical and operational data from multiple sources
- **Real-time Metrics**: Automated calculation of key performance indicators
- **Data Quality Index**: Composite scoring system for trial readiness assessment
- **Generative AI**: Natural language summaries and automated report generation
- **Agentic AI**: Role-based intelligent agents for proactive risk detection
- **Interactive Dashboards**: Role-specific views for Trial Managers, CRAs, and Data Managers
- **Upload & Analyze**: Upload your own clinical trial data files and get instant AI-powered insights

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. The system is pre-configured with Gemini AI integration via the .env file

## Project Structure
```
NestTry/
├── src/
│   ├── ingestion/          # Data ingestion and loading
│   ├── harmonization/      # Canonical data model
│   ├── metrics/            # Metric calculation engine
│   ├── intelligence/       # Risk detection and insights
│   ├── ai/                 # Generative and Agentic AI
│   └── dashboard/          # Streamlit UI
├── data/                   # Input data files
├── output/                 # Generated reports
├── tests/                  # Test suite
└── docs/                   # Documentation
```

## Usage

### Run the Dashboard
```bash
streamlit run src/dashboard/app.py
```

### Upload Your Own Data
1. Navigate to the "📤 Upload & Analyze" page in the dashboard
2. Enter a study name
3. Upload your Excel files (Missing Pages Reports, Visit Trackers, EDRR, SAE Dashboard, Coding Reports)
4. Click "Analyze Data" to get instant insights
5. View comprehensive analysis across multiple tabs
6. Export results as CSV files

### Process Data Programmatically
```bash
python src/main.py
```

## Key Components

### 1. Data Ingestion Layer
Loads and validates clinical trial reports from multiple sources.

### 2. Harmonization Layer
Creates a unified canonical model across all data sources.

### 3. Metrics Engine
Calculates derived metrics including:
- Missing visits/pages percentages
- Query resolution rates
- SDV completion status
- Clean patient indicators

### 4. Data Quality Index
Composite scoring system with configurable weights for:
- Safety issues (highest priority)
- Missing visits
- Open queries
- Coding delays

### 5. AI Intelligence
- **Generative AI**: Natural language summaries and explanations
- **Agentic AI**: Role-based agents (CRA, Data Quality, Trial Manager)

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
Follow PEP 8 guidelines. Format code with:
```bash
black src/
```

## License
Proprietary - Hackathon Submission

## Authors
Team NestTry - NEST 2.0 Hackathon

## Acknowledgments
Built for Real-Time Operational Dataflow Metrics for Clinical Trials challenge.
