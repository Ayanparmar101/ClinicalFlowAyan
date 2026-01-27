# Clinical Trial Intelligence Platform
## Technical Architecture Documentation

## Overview
The Clinical Trial Intelligence Platform is an enterprise-grade solution that transforms fragmented clinical trial operational reports into actionable intelligence using Generative and Agentic AI.

## System Architecture

### Layer 1: Data Ingestion
**Purpose**: Load and validate clinical trial data from Excel files

**Components**:
- `DataIngestionEngine`: Main ingestion orchestrator
- File type classification based on naming patterns
- Metadata tracking (timestamps, source files)
- Error handling and validation

**Key Features**:
- Supports both .xlsx and .xls formats
- Auto-discovery of study folders
- Incremental snapshot versioning
- Audit trail for regulatory compliance

**Data Sources Supported**:
- EDC Metrics (CPID)
- Missing Pages Reports
- SAE Dashboards
- Coding Reports (MedDRA, WHODrug)
- Lab Reports
- Visit Projection Trackers
- Inactivated Forms
- EDRR Compilations

### Layer 2: Harmonization & Canonical Model
**Purpose**: Create unified data model from heterogeneous sources

**Components**:
- `CanonicalDataModel`: Core harmonization engine
- Column standardization mappings
- Entity extraction logic

**Canonical Entities**:
1. **Study**: Protocol-level information
2. **Site**: Investigational site details
3. **Subject**: Patient-level data
4. **Visit**: Visit completion status
5. **Safety Events**: SAE tracking
6. **Lab Data**: Laboratory findings
7. **Coding Data**: Medical terminology

**Key Features**:
- Flexible column mapping
- Referential integrity enforcement
- Temporal alignment
- Unified patient view generation

### Layer 3: Metrics Engine
**Purpose**: Calculate derived metrics and performance indicators

**Components**:
- `MetricsEngine`: Main metrics calculation engine
- Subject-level metrics calculator
- Site-level aggregation logic
- Study-level summaries

**Calculated Metrics**:

**Completeness Metrics**:
- % Missing visits
- % Missing pages
- Overall completeness score

**Query Metrics**:
- Open vs closed queries
- Query resolution rate
- Query aging
- High query burden flags

**SDV Metrics**:
- SDV completion status
- % SDV complete by site

**Safety Metrics**:
- Total SAEs
- Open vs closed SAEs
- Overdue follow-ups

**Site Performance Metrics**:
- Weighted performance score
- Subject count
- Aggregated data quality indicators

### Layer 4: Data Quality Index (DQI)
**Purpose**: Composite scoring system for data quality assessment

**Components**:
- `DataQualityIndex`: DQI calculation engine
- Component scoring logic
- Risk classification rules

**DQI Components & Weights**:
1. Safety Issues: 35% (highest priority)
2. Missing Visits: 25%
3. Open Queries: 20%
4. Missing Pages: 10%
5. Coding Delays: 5%
6. SDV Incomplete: 5%

**Risk Thresholds**:
- High Risk: DQI < 70
- Medium Risk: 70 ≤ DQI < 85
- Low Risk: DQI ≥ 85

**Clean Patient Criteria**:
A patient is "clean" only if ALL of the following are true:
- Zero missing visits
- Zero missing pages
- Zero open queries
- Zero pending SDV
- Zero open safety issues

**Key Features**:
- Transparent scoring methodology
- Configurable weights
- Subject, site, and study-level DQI
- Critical issue identification

### Layer 5: Risk Intelligence
**Purpose**: Proactive detection of operational bottlenecks and risks

**Components**:
- `RiskIntelligence`: Pattern detection engine
- Trend analysis logic
- Readiness assessment rules

**Risk Detection Capabilities**:

**High-Risk Site Detection**:
- Performance score below threshold
- Multiple risk factors identified
- Site-specific risk factor analysis

**High-Risk Subject Detection**:
- DQI-based classification
- Individual risk factor identification
- Priority flagging

**Query Hotspots**:
- Sites with concentrated query issues
- Severity classification
- Affected subject counts

**Interim Analysis Readiness**:
- Multi-criterion assessment
- Blocking issue identification
- Warning generation
- Recommendation engine

**Trend Detection**:
- Historical performance comparison
- Worsening/improving trend identification
- Magnitude of change analysis

### Layer 6: Generative AI
**Purpose**: Natural language summaries, explanations, and report generation

**Components**:
- `GenerativeAI`: LLM integration layer
- Prompt engineering templates
- Fallback response handling

**Capabilities**:

**Study Performance Summaries**:
- Executive-level summaries
- Key concerns identification
- Readiness assessment

**Site Performance Summaries**:
- Operational efficiency analysis
- Data quality assessment
- CRA-focused insights

**CRA Report Generation**:
- Portfolio status
- Sites requiring attention
- Recommended actions

**DQI Explanations**:
- Component breakdown
- Root cause identification
- Improvement recommendations

**Natural Language Querying**:
- Context-aware answers
- Data-driven responses
- Citation of source metrics

**Key Features**:
- OpenAI GPT-4 integration
- Configurable temperature and max tokens
- Fallback mode when API unavailable
- Professional, domain-specific tone

### Layer 7: Agentic AI
**Purpose**: Role-based intelligent agents providing proactive recommendations

**Agent Types**:

#### 1. CRA Agent
**Responsibilities**:
- Monitor assigned sites
- Analyze backlogs
- Prioritize monitoring visits
- Generate action recommendations

**Capabilities**:
- Overdue visit detection
- Query burden analysis
- Performance-based escalation
- Visit focus area identification

**Outputs**:
- Prioritized site list
- Action recommendations with priority
- Visit scheduling suggestions

#### 2. Data Quality Agent
**Responsibilities**:
- Monitor data quality across studies
- Detect systemic issues
- Recommend improvement strategies

**Capabilities**:
- Systemic pattern detection
- Query resolution strategy
- Training gap identification
- Resource allocation recommendations

**Outputs**:
- Systemic issue reports
- Resolution timelines
- Resource requirements

#### 3. Trial Manager Agent
**Responsibilities**:
- Monitor overall study health
- Assess milestone risks
- Recommend resource allocation

**Capabilities**:
- Milestone risk assessment
- Multi-criterion evaluation
- Resource distribution optimization
- Executive briefing generation

**Outputs**:
- Risk assessments
- Blocking issue lists
- Strategic recommendations
- Executive briefings

**Key Features**:
- Recommendation-only (human-in-the-loop)
- Context-aware decision support
- Priority and severity classification
- Audit trail of recommendations

### Layer 8: User Experience & Dashboard
**Purpose**: Interactive visualization and role-based dashboards

**Technology Stack**:
- Streamlit for web interface
- Plotly for interactive visualizations
- Pandas for data manipulation

**Dashboard Views**:

#### Executive Dashboard
- Portfolio-level KPIs
- Study comparison charts
- Risk distribution visualizations
- Trend analysis

#### Study Analysis
- Detailed study metrics
- DQI distribution
- Risk breakdown
- Site performance
- AI insights

#### CRA Dashboard (Future)
- Assigned site list
- Action backlogs
- Visit priorities

**Key Features**:
- Real-time data updates (via cache)
- Drill-down capability
- Interactive filtering
- Export functionality
- Responsive design

## Data Flow

```
Raw Excel Files
    ↓
Data Ingestion Engine
    ↓
Canonical Data Model
    ↓
Metrics Engine
    ↓
Data Quality Index
    ↓
Risk Intelligence
    ↓
AI Layers (Generative + Agentic)
    ↓
Interactive Dashboard / Reports
```

## Governance & Compliance

### Audit Trail
Every operation is logged with:
- Timestamp
- Source file
- User/process
- Operations performed

### Data Lineage
Complete traceability from:
- Source file → Canonical entity → Metric → Insight

### Read-Only Architecture
- Platform does not modify source systems
- Intelligence layer only
- No autonomous actions

### Role-Based Access Control
- Configurable user permissions
- Study-level access controls
- Action approval workflows

## Scalability Considerations

### Performance
- Efficient pandas operations
- Cached computations
- Incremental processing support

### Multi-Study Support
- Study-agnostic design
- Parallel processing capability
- Aggregated portfolio views

### Extensibility
- Modular architecture
- Plugin-ready design
- Configurable rules and weights

## Security

### API Key Management
- Environment variable configuration
- No hardcoded credentials
- Secure storage recommendations

### Data Protection
- Local processing (no external data transfer)
- Configurable data retention
- Anonymization support

## Future Enhancements

### Phase 2 (Days 91-180)
- Real-time data streaming
- Automated report scheduling
- Mobile-responsive dashboards
- Enhanced collaboration features

### Phase 3 (Days 181-270)
- Predictive analytics
- Machine learning models
- Integration with EDC systems
- Advanced workflow automation

## Deployment

### Local Deployment
```bash
pip install -r requirements.txt
python src/main.py
streamlit run src/dashboard/app.py
```

### Enterprise Deployment
- Docker containerization
- Kubernetes orchestration
- Load balancing
- High availability setup

## Monitoring & Maintenance

### Logs
- Application logs: `logs/`
- Error tracking
- Performance metrics

### Health Checks
- Data ingestion status
- Metric calculation success rate
- AI service availability

## Support & Documentation

### Code Documentation
- Inline docstrings
- Type hints
- Example usage

### User Guides
- Getting started guide
- Role-specific guides
- FAQ

## Technology Stack Summary

**Backend**:
- Python 3.9+
- Pandas
- NumPy
- OpenAI API

**Frontend**:
- Streamlit
- Plotly
- HTML/CSS

**Data Storage**:
- File-based (Excel)
- CSV exports
- Future: PostgreSQL/MongoDB

**AI/ML**:
- OpenAI GPT-4
- LangChain (future)
- Custom algorithms

## License
Proprietary - NEST 2.0 Hackathon Submission

## Contact
Team NestTry - NEST 2.0 Hackathon
