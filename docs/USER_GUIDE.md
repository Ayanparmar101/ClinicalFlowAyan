# User Guide
## Clinical Trial Intelligence Platform

## Table of Contents
1. [Getting Started](#getting-started)
2. [Data Preparation](#data-preparation)
3. [Running the Platform](#running-the-platform)
4. [Understanding the Dashboard](#understanding-the-dashboard)
5. [Interpreting Metrics](#interpreting-metrics)
6. [AI Features](#ai-features)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites
- Python 3.9 or higher
- Excel files (.xlsx or .xls) containing clinical trial data
- (Optional) OpenAI API key for AI features

### Installation

1. **Install dependencies**:
   ```bash
   cd NestTry
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Verify installation**:
   ```bash
   python src/main.py --help
   ```

## Data Preparation

### Required Data Structure

Place your data files in the following structure:
```
NestTry/
└── data/
    ├── Study 2/
    │   ├── CPID_EDC_Metrics.xlsx
    │   ├── Missing_Pages_Report.xlsx
    │   ├── SAE_Dashboard.xlsx
    │   └── ...
    ├── Study 17/
    │   └── ...
    └── Study 18/
        └── ...
```

### Supported File Types

The platform automatically detects and classifies:

- **EDC Metrics**: Files containing "EDC_Metrics" or "CPID"
- **Missing Pages**: Files containing "Missing_Pages"
- **SAE Dashboard**: Files containing "SAE" and "Dashboard"
- **Coding Reports**: Files containing "Coding", "MedDRA", or "WHO"
- **Lab Reports**: Files containing "Lab" and "Missing" or "Range"
- **Visit Projections**: Files containing "Visit_Projection"
- **Inactivated Forms**: Files containing "Inactivated"
- **EDRR**: Files containing "EDRR"

### Data Quality Requirements

**Minimum Required Columns**:

**EDC Metrics**:
- Subject ID
- Site ID
- Visits Expected / Visits Completed
- Pages Expected / Pages Completed
- Open Queries / Closed Queries

**Missing Pages**:
- Subject ID
- Visit Name
- Page Name

**SAE Dashboard**:
- Subject ID
- Status (Open/Closed)

## Running the Platform

### Method 1: Command Line Processing

Process all data and generate exports:
```bash
python src/main.py
```

This will:
1. Ingest all data from `/data`
2. Calculate all metrics
3. Generate DQI scores
4. Perform risk analysis
5. Export results to `/output`

**Output Location**: `NestTry/output/`

### Method 2: Interactive Dashboard

Launch the web-based dashboard:
```bash
streamlit run src/dashboard/app.py
```

This will:
- Start a local web server
- Open your browser automatically
- Provide interactive visualizations
- Enable drill-down analysis

**Default URL**: `http://localhost:8501`

## Understanding the Dashboard

### Executive Dashboard

**Purpose**: High-level portfolio view for senior management

**Key Metrics**:
- Total Studies
- Total Subjects
- Portfolio DQI (average across all subjects)
- Clean Data Rate (% of subjects meeting all criteria)

**Visualizations**:
- Study comparison bar chart (DQI by study)
- Summary table with key metrics per study

**Use Cases**:
- Portfolio health check
- Cross-study comparison
- Executive reporting

### Study Analysis

**Purpose**: Deep dive into individual study performance

**Sections**:

#### 1. Metrics Tab
- DQI score distribution histogram
- Risk level pie chart
- Data completeness box plots
- Query statistics

**Key Insights**:
- Are most subjects high or low risk?
- What's the average completeness?
- Where are the data gaps?

#### 2. Risk Analysis Tab
- High-risk subjects table (top 10 by lowest DQI)
- Query hotspots (sites with concentrated issues)
- Individual risk factor breakdown

**Key Insights**:
- Which subjects need immediate attention?
- Which sites have query management issues?
- What are the primary risk drivers?

#### 3. Site View Tab
- Site performance bar chart
- Site metrics table with all KPIs

**Key Insights**:
- Which sites are underperforming?
- Where should CRAs focus?
- Are there geographic patterns?

#### 4. AI Insights Tab
- AI-generated study summaries
- Data Quality Agent recommendations
- Trial Manager risk assessments

**Key Insights**:
- Natural language interpretation
- Prioritized action items
- Milestone risk predictions

## Interpreting Metrics

### Data Quality Index (DQI)

**Scale**: 0-100 (higher is better)

**Interpretation**:
- **85-100 (Low Risk)**: Excellent data quality, ready for analysis
- **70-84 (Medium Risk)**: Some concerns, targeted improvements needed
- **Below 70 (High Risk)**: Significant issues, immediate action required

**Component Weights**:
- Safety Issues: 35% (most important)
- Missing Visits: 25%
- Open Queries: 20%
- Missing Pages: 10%
- Coding Delays: 5%
- SDV Incomplete: 5%

**Example**:
- Subject with DQI 65 likely has:
  - Unresolved safety event OR
  - Multiple missing visits OR
  - High query count

### Clean Patient Status

**Definition**: A patient is "clean" only if ALL of the following are true:
- ✅ No missing visits
- ✅ No missing pages
- ✅ No open queries
- ✅ SDV complete
- ✅ No open safety issues

**Study Readiness**:
- **< 75% clean**: Not ready for analysis
- **75-90% clean**: Conditionally ready with disclaimers
- **> 90% clean**: Ready for interim analysis or submission

### Performance Score (Sites)

**Scale**: 0-100 (higher is better)

**Calculation**: Weighted combination of:
- Missing visits (high weight)
- Missing pages (medium weight)
- Open queries (high weight)

**Thresholds**:
- **< 70**: High priority for CRA attention
- **70-85**: Standard monitoring
- **> 85**: Low touch, routine visits

## AI Features

### Generative AI Summaries

**Purpose**: Natural language interpretation of metrics

**How to Use**:
1. Navigate to Study Analysis → AI Insights tab
2. Click "Generate Study Summary"
3. Review AI-generated narrative

**Example Output**:
> "Study 18 shows moderate data quality with 78% clean patients. Primary concerns include 45 unresolved queries concentrated at 3 sites, and 12% missing page rate. Recommend targeted query resolution campaign before proceeding to database lock."

### Agentic AI Recommendations

**Purpose**: Proactive, role-based action suggestions

**Agent Types**:

#### Data Quality Agent
**Focuses on**:
- Systemic data issues
- Query management
- Training gaps

**Example Recommendations**:
- "High query rate detected: Implement query resolution training"
- "30% of subjects have incomplete SDV: Increase monitoring resources"

#### Trial Manager Agent
**Focuses on**:
- Milestone readiness
- Resource allocation
- Risk assessment

**Example Recommendations**:
- "Database lock at risk: 22% subjects not clean, 60 days remaining"
- "Reallocate CRA resources: 3 sites require intensive monitoring"

### Configuring AI

**OpenAI API Key** (required for full AI features):
1. Obtain key from https://platform.openai.com/
2. Edit `.env` file:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
3. Restart application

**Fallback Mode**:
If no API key configured, platform still works but:
- AI summaries show placeholder messages
- Agents use rule-based logic only
- No natural language generation

## Troubleshooting

### Common Issues

#### 1. "No data found" Error

**Cause**: Data files not in correct location

**Solution**:
- Verify files are in `NestTry/data/StudyX/` structure
- Check file extensions (.xlsx or .xls)
- Ensure study folders are named "Study X" format

#### 2. "Column not found" Error

**Cause**: Expected columns missing from source files

**Solution**:
- Review column mappings in `config.py`
- Ensure required columns exist:
  - Subject ID (or variations)
  - Site ID
  - Visits Expected/Completed
  - Pages Expected/Completed

#### 3. Dashboard Not Loading

**Cause**: Port conflict or missing dependencies

**Solution**:
```bash
# Try different port
streamlit run src/dashboard/app.py --server.port 8502

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

#### 4. AI Features Not Working

**Cause**: API key not configured or invalid

**Solution**:
- Check `.env` file has valid OpenAI key
- Verify internet connection
- Check OpenAI API status

### Getting Help

**Logs Location**: `NestTry/logs/`

**Check Logs**:
```bash
# View latest log
tail -f logs/ctip_*.log
```

**Contact**: [Your team contact information]

## Best Practices

### For Data Managers
1. Run full processing daily to track trends
2. Focus on DQI < 70 subjects first
3. Use query hotspot view to prioritize sites
4. Export results for study team meetings

### For CRAs
1. Check assigned sites in CRA dashboard
2. Prioritize visits based on performance scores
3. Use AI recommendations for visit planning
4. Review high-risk subjects before site visits

### For Trial Managers
1. Review executive dashboard weekly
2. Monitor milestone risk assessments
3. Use AI briefings for stakeholder updates
4. Track portfolio DQI trends

### For Sponsors
1. Compare studies using executive view
2. Identify systemic issues across portfolio
3. Use insights for resourcing decisions
4. Track readiness for regulatory milestones

## Next Steps

After mastering the basics:
1. Explore advanced filtering in dashboard
2. Customize DQI weights for your needs
3. Integrate with existing workflows
4. Request additional features

## Appendix

### Glossary

- **DQI**: Data Quality Index
- **CRA**: Clinical Research Associate
- **SAE**: Serious Adverse Event
- **SDV**: Source Data Verification
- **EDC**: Electronic Data Capture
- **CRF**: Case Report Form
- **EDRR**: Electronic Data Review & Reconciliation

### Keyboard Shortcuts (Dashboard)

- `Ctrl+R`: Refresh data
- `F11`: Full screen mode
- `Ctrl+S`: Export current view (browser save)

### Performance Tips

- Limit dashboard to 1-2 studies for fastest loading
- Use CLI processing for large portfolios
- Clear browser cache if visualizations lag
- Process data overnight for morning reviews
