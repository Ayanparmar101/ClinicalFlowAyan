"""
Main Streamlit Dashboard Application
Interactive dashboard for the Clinical Trial Intelligence Platform
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from ingestion import DataIngestionEngine
from harmonization import CanonicalDataModel
from metrics import MetricsEngine, DataQualityIndex
from intelligence import RiskIntelligence
from ai import GenerativeAI, CRAAgent, DataQualityAgent, TrialManagerAgent
from config import DATA_PATH, APP_NAME, APP_VERSION

# Page configuration
st.set_page_config(
    page_title="Clinical Trial Intelligence Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .risk-high {
        color: #d62728;
        font-weight: bold;
    }
    .risk-medium {
        color: #ff7f0e;
        font-weight: bold;
    }
    .risk-low {
        color: #2ca02c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_and_process_data(_version=5):  # Increment this to bust cache
    """Load and process all clinical trial data"""
    with st.spinner("Loading clinical trial data..."):
        # Ingestion - now uses multi-file loader
        ingestion_engine = DataIngestionEngine(DATA_PATH)
        studies = ingestion_engine.discover_studies()
        
        all_data = {}
        for study_name in studies:
            study_df = ingestion_engine.load_study_data(study_name)
            if study_df is not None and not study_df.empty:
                all_data[study_name] = study_df
        
        # Check for uploaded data in session state
        if 'uploaded_study_name' in st.session_state and st.session_state.uploaded_study_name:
            all_data[st.session_state.uploaded_study_name] = st.session_state.uploaded_study_df
        
        if not all_data:
            return None, None, None, None
        
        # Harmonization - skip for now since data is already consolidated
        canonical_model = CanonicalDataModel()
        canonical_entities = canonical_model.build_canonical_model(all_data)
        
        # Metrics calculation - data already has metrics, just need to format
        metrics_engine = MetricsEngine(canonical_entities, all_data)
        all_metrics = {}
        
        for study_name in all_data.keys():
            study_metrics = metrics_engine.calculate_all_metrics_for_study(study_name)
            all_metrics[study_name] = study_metrics
        
        # Calculate DQI
        dqi_calculator = DataQualityIndex()
        for study_name, metrics in all_metrics.items():
            if "subject_metrics" in metrics:
                metrics["subject_metrics"] = dqi_calculator.calculate_subject_dqi(
                    metrics["subject_metrics"]
                )
        
        # Risk intelligence
        risk_engine = RiskIntelligence(all_metrics)
        
        return all_data, all_metrics, canonical_entities, risk_engine


def render_header():
    """Render application header"""
    st.markdown(f'<div class="main-header">🔬 {APP_NAME}</div>', unsafe_allow_html=True)
    st.markdown(f"<center><i>Version {APP_VERSION} - Real-Time Operational Dataflow Metrics</i></center>", 
                unsafe_allow_html=True)
    st.markdown("---")


def render_executive_dashboard(all_metrics, risk_engine):
    """Render executive dashboard view"""
    st.header("📊 Executive Dashboard")
    
    if not all_metrics:
        st.info("📤 No data loaded yet. Go to **'Upload & Analyze'** to upload your study files and view them here!")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_studies = len(all_metrics)
    total_subjects = sum(m.get("subject_metrics", pd.DataFrame()).shape[0] for m in all_metrics.values())
    
    # Calculate portfolio metrics
    all_subject_data = []
    for study_metrics in all_metrics.values():
        if "subject_metrics" in study_metrics:
            all_subject_data.append(study_metrics["subject_metrics"])
    
    if all_subject_data:
        portfolio_df = pd.concat(all_subject_data, ignore_index=True)
        avg_dqi = portfolio_df["dqi_score"].mean() if "dqi_score" in portfolio_df.columns else 0
        high_risk_count = (portfolio_df["risk_level"] == "High").sum() if "risk_level" in portfolio_df.columns else 0
        clean_count = portfolio_df["is_clean_patient"].sum() if "is_clean_patient" in portfolio_df.columns else 0
        pct_clean = (clean_count / len(portfolio_df) * 100) if len(portfolio_df) > 0 else 0
    else:
        avg_dqi = 0
        high_risk_count = 0
        pct_clean = 0
    
    with col1:
        st.metric("Total Studies", total_studies)
    with col2:
        st.metric("Total Subjects", total_subjects)
    with col3:
        st.metric("Portfolio DQI", f"{avg_dqi:.1f}/100")
    with col4:
        st.metric("Clean Data Rate", f"{pct_clean:.1f}%")
    
    st.markdown("---")
    
    # Study comparison
    st.subheader("Study Performance Comparison")
    
    study_summary_data = []
    for study_name, metrics in all_metrics.items():
        if "subject_metrics" in metrics:
            df = metrics["subject_metrics"]
            summary = {
                "Study": study_name,
                "Subjects": len(df),
                "Avg DQI": df["dqi_score"].mean() if "dqi_score" in df.columns else 0,
                "High Risk": (df["risk_level"] == "High").sum() if "risk_level" in df.columns else 0,
                "% Clean": (df["is_clean_patient"].sum() / len(df) * 100) if "is_clean_patient" in df.columns else 0
            }
            study_summary_data.append(summary)
    
    if study_summary_data:
        study_summary_df = pd.DataFrame(study_summary_data)
        
        # Bar chart
        fig = px.bar(study_summary_df, x="Study", y="Avg DQI", 
                     title="Data Quality Index by Study",
                     labels={"Avg DQI": "Average DQI Score"},
                     color="Avg DQI",
                     color_continuous_scale="RdYlGn")
        st.plotly_chart(fig, width='stretch')
        
        # Data table
        st.dataframe(study_summary_df, use_container_width=True)


def render_study_view(all_metrics, risk_engine):
    """Render detailed study view"""
    st.header("🔍 Study Analysis")
    
    if not all_metrics:
        st.info("📤 No data loaded yet. Go to **'Upload & Analyze'** to upload your study files and view them here!")
        return
    
    # Study selector
    selected_study = st.selectbox("Select Study", list(all_metrics.keys()))
    
    if selected_study not in all_metrics:
        return
    
    study_metrics = all_metrics[selected_study]
    
    # Study summary
    st.subheader(f"Study: {selected_study}")
    
    if "subject_metrics" in study_metrics:
        subject_df = study_metrics["subject_metrics"]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Subjects", len(subject_df))
        with col2:
            clean_count = subject_df["is_clean_patient"].sum() if "is_clean_patient" in subject_df.columns else 0
            st.metric("Clean Patients", clean_count)
        with col3:
            avg_dqi = subject_df["dqi_score"].mean() if "dqi_score" in subject_df.columns else 0
            st.metric("Avg DQI", f"{avg_dqi:.1f}")
        with col4:
            high_risk = (subject_df["risk_level"] == "High").sum() if "risk_level" in subject_df.columns else 0
            st.metric("High Risk", high_risk, delta_color="inverse")
        with col5:
            total_queries = subject_df["open_queries"].sum() if "open_queries" in subject_df.columns else 0
            st.metric("Open Queries", int(total_queries))
        
        st.markdown("---")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Metrics", "⚠️ Risk Analysis", "🗺️ Site View", "🤖 AI Insights"])
        
        with tab1:
            render_study_metrics(subject_df, study_metrics)
        
        with tab2:
            render_risk_analysis(subject_df, risk_engine, selected_study)
        
        with tab3:
            render_site_analysis(subject_df, study_metrics)
        
        with tab4:
            render_ai_insights(selected_study, subject_df, study_metrics)


def render_study_metrics(subject_df, study_metrics):
    """Render study metrics visualizations"""
    st.subheader("Key Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # DQI distribution
        if "dqi_score" in subject_df.columns:
            fig = px.histogram(subject_df, x="dqi_score", 
                             title="DQI Score Distribution",
                             labels={"dqi_score": "DQI Score"},
                             nbins=20)
            st.plotly_chart(fig, width='stretch')
    
    with col2:
        # Risk level distribution
        if "risk_level" in subject_df.columns:
            risk_counts = subject_df["risk_level"].value_counts()
            fig = px.pie(values=risk_counts.values, names=risk_counts.index,
                        title="Risk Level Distribution",
                        color_discrete_map={"High": "#d62728", "Medium": "#ff7f0e", "Low": "#2ca02c"})
            st.plotly_chart(fig, width='stretch')
    
    # Completeness metrics
    if all(col in subject_df.columns for col in ["pct_missing_visits", "pct_missing_pages"]):
        st.subheader("Data Completeness")
        
        col1, col2 = st.columns(2)
        
        with col1:
            avg_missing_visits = subject_df["pct_missing_visits"].mean()
            st.metric("Avg Missing Visits", f"{avg_missing_visits:.1f}%")
            
            fig = px.box(subject_df, y="pct_missing_visits",
                        title="Missing Visits Distribution")
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            avg_missing_pages = subject_df["pct_missing_pages"].mean()
            st.metric("Avg Missing Pages", f"{avg_missing_pages:.1f}%")
            
            fig = px.box(subject_df, y="pct_missing_pages",
                        title="Missing Pages Distribution")
            st.plotly_chart(fig, width='stretch')


def render_risk_analysis(subject_df, risk_engine, study_name):
    """Render risk analysis"""
    st.subheader("Risk Analysis")
    
    # High risk subjects
    if "risk_level" in subject_df.columns:
        high_risk_subjects = subject_df[subject_df["risk_level"] == "High"]
        
        st.write(f"**High Risk Subjects: {len(high_risk_subjects)}**")
        
        if not high_risk_subjects.empty:
            # Show top 10 by lowest DQI
            if "dqi_score" in high_risk_subjects.columns:
                top_risk = high_risk_subjects.nsmallest(10, "dqi_score")
                
                display_cols = ["Subject ID", "Site ID", "dqi_score", "risk_level", 
                               "open_queries", "missing_visits", "missing_pages"]
                display_cols = [col for col in display_cols if col in top_risk.columns]
                
                st.dataframe(top_risk[display_cols], use_container_width=True)
        
        # Query hotspots
        st.subheader("Query Hotspots")
        if "Site ID" in subject_df.columns and "open_queries" in subject_df.columns:
            hotspot_summary = subject_df[subject_df["open_queries"] >= 3].groupby("Site ID").agg({
                "Subject ID": "count",
                "open_queries": "sum"
            }).reset_index()
            hotspot_summary.columns = ["Site ID", "Affected Subjects", "Total Open Queries"]
            hotspot_summary = hotspot_summary.sort_values("Total Open Queries", ascending=False)
            
            if not hotspot_summary.empty:
                st.dataframe(hotspot_summary, use_container_width=True)
            else:
                st.success("No query hotspots detected")


def render_site_analysis(subject_df, study_metrics):
    """Render site-level analysis"""
    st.subheader("Site Performance")
    
    if "site_metrics" in study_metrics:
        site_df = study_metrics["site_metrics"]
        
        # Performance chart
        if "performance_score" in site_df.columns:
            fig = px.bar(site_df, x="site_id", y="performance_score",
                        title="Site Performance Scores",
                        labels={"performance_score": "Performance Score", "site_id": "Site ID"},
                        color="performance_score",
                        color_continuous_scale="RdYlGn")
            st.plotly_chart(fig, width='stretch')
        
        # Site metrics table
        st.dataframe(site_df, use_container_width=True)
    else:
        st.info("Site-level metrics not available")


def render_ai_insights(study_name, subject_df, study_metrics):
    """Render AI-generated insights"""
    st.subheader("🤖 AI-Powered Insights")
    
    st.info("AI insights are powered by Gemini AI. Configuration is set in .env file.")
    
    # Generate summary metrics for AI
    summary = {
        "total_subjects": len(subject_df),
        "clean_subjects": subject_df["is_clean_patient"].sum() if "is_clean_patient" in subject_df.columns else 0,
        "pct_clean": (subject_df["is_clean_patient"].sum() / len(subject_df) * 100) if "is_clean_patient" in subject_df.columns else 0,
        "avg_completeness": subject_df["completeness_score"].mean() if "completeness_score" in subject_df.columns else 0,
        "total_open_queries": subject_df["open_queries"].sum() if "open_queries" in subject_df.columns else 0
    }
    
    # Initialize AI
    gen_ai = GenerativeAI()
    
    if st.button("Generate Study Summary"):
        with st.spinner("Generating AI summary..."):
            summary_text = gen_ai.summarize_study_performance(study_name, summary)
            st.write(summary_text)
    
    # Agent recommendations
    st.subheader("Agent Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Data Quality Agent**")
        dq_agent = DataQualityAgent(gen_ai)
        issues = dq_agent.detect_systemic_issues(subject_df)
        
        if issues:
            for issue in issues:
                st.warning(f"**{issue['category']}**: {issue['reason']}")
                st.write(f"*Action*: {issue['action']}")
        else:
            st.success("No systemic issues detected")
    
    with col2:
        st.write("**Trial Manager Agent**")
        tm_agent = TrialManagerAgent(study_name, gen_ai)
        
        from datetime import datetime, timedelta
        milestone_date = datetime.now() + timedelta(days=60)
        
        assessment = tm_agent.assess_milestone_risk(summary, "Database Lock", milestone_date)
        
        risk_color = "🔴" if assessment["risk_level"] == "High" else "🟡" if assessment["risk_level"] == "Medium" else "🟢"
        st.write(f"{risk_color} **Risk Level**: {assessment['risk_level']}")
        st.write(f"**Days to Milestone**: {assessment['days_remaining']}")
        
        if assessment["blocking_issues"]:
            st.write("**Blocking Issues:**")
            for issue in assessment["blocking_issues"]:
                st.write(f"- {issue}")


def render_cra_dashboard(all_data, all_metrics, canonical_entities, risk_engine):
    """Render CRA-specific dashboard for site monitoring and operational excellence"""
    st.header("👨‍⚕️ Clinical Research Associate Dashboard")
    st.markdown("**Site Monitoring & Operational Excellence**")
    st.markdown("---")
    
    if not all_metrics:
        st.info("📤 No data loaded yet. Go to **'Upload & Analyze'** to upload your study files and view them here!")
        return
    
    # Study selector
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_study = st.selectbox("Select Study for Monitoring", list(all_metrics.keys()))
    with col2:
        st.metric("Active Studies", len(all_metrics))
    
    if selected_study not in all_metrics:
        return
    
    study_metrics = all_metrics[selected_study]
    study_data = all_data.get(selected_study, pd.DataFrame())
    
    # Top-level CRA metrics
    st.subheader("📊 Study Overview")
    
    if "subject_metrics" in study_metrics and "site_metrics" in study_metrics:
        subject_df = study_metrics["subject_metrics"]
        site_df = study_metrics["site_metrics"]
        safety = study_metrics.get("safety_metrics", {})
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            total_sites = len(site_df)
            st.metric("Total Sites", total_sites)
        
        with col2:
            total_subjects = len(subject_df)
            st.metric("Total Subjects", total_subjects)
        
        with col3:
            total_queries = int(subject_df["open_queries"].sum()) if "open_queries" in subject_df.columns else 0
            st.metric("Open Queries", total_queries, delta="Urgent" if total_queries > 50 else None)
        
        with col4:
            total_missing_visits = int(subject_df["missing_visits"].sum()) if "missing_visits" in subject_df.columns else 0
            st.metric("Missing Visits", total_missing_visits, delta="Alert" if total_missing_visits > 10 else None)
        
        with col5:
            high_risk_subjects = (subject_df["risk_level"] == "High").sum() if "risk_level" in subject_df.columns else 0
            st.metric("High Risk Subjects", high_risk_subjects, delta_color="inverse")
        
        with col6:
            clean_pct = (subject_df["is_clean_patient"].sum() / len(subject_df) * 100) if "is_clean_patient" in subject_df.columns and len(subject_df) > 0 else 0
            st.metric("Clean Data Rate", f"{clean_pct:.1f}%")
        
        st.markdown("---")
        
        # Create tabs for different CRA views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🏥 Site Performance",
            "📝 Query Management", 
            "📅 Visit Compliance",
            "⚠️ Action Items",
            "📊 Analytics"
        ])
        
        with tab1:
            render_cra_site_performance(site_df, subject_df, study_data)
        
        with tab2:
            render_cra_query_management(subject_df, site_df)
        
        with tab3:
            render_cra_visit_compliance(subject_df, site_df)
        
        with tab4:
            render_cra_action_items(subject_df, site_df, study_metrics, risk_engine, selected_study)
        
        with tab5:
            render_cra_analytics(subject_df, site_df, study_metrics)
    else:
        st.warning("Required metrics not available for this study.")


def render_cra_site_performance(site_df, subject_df, study_data):
    """Render site performance monitoring view"""
    st.subheader("🏥 Site Performance Dashboard")
    
    # Site performance summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Performance Distribution**")
        if "performance_score" in site_df.columns:
            # Categorize sites
            high_perf = len(site_df[site_df["performance_score"] >= 80])
            med_perf = len(site_df[(site_df["performance_score"] >= 60) & (site_df["performance_score"] < 80)])
            low_perf = len(site_df[site_df["performance_score"] < 60])
            
            perf_data = pd.DataFrame({
                "Category": ["High (≥80)", "Medium (60-79)", "Low (<60)"],
                "Count": [high_perf, med_perf, low_perf]
            })
            
            fig = px.bar(perf_data, x="Category", y="Count",
                        color="Category",
                        color_discrete_map={"High (≥80)": "#2ca02c", "Medium (60-79)": "#ff7f0e", "Low (<60)": "#d62728"},
                        title="Site Performance Categories")
            st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.write("**Top 5 Performing Sites**")
        if "performance_score" in site_df.columns:
            top_sites = site_df.nlargest(5, "performance_score")[["site_id", "performance_score", "subject_count"]]
            st.dataframe(top_sites, hide_index=True, use_container_width=True)
        
        st.write("**Bottom 5 Sites (Need Attention)**")
        if "performance_score" in site_df.columns:
            bottom_sites = site_df.nsmallest(5, "performance_score")[["site_id", "performance_score", "subject_count"]]
            st.dataframe(bottom_sites, hide_index=True, use_container_width=True)
    
    # Detailed site performance chart
    st.write("**Detailed Site Performance**")
    if "performance_score" in site_df.columns:
        # Sort by performance score
        site_df_sorted = site_df.sort_values("performance_score", ascending=False)
        
        fig = go.Figure()
        
        # Add bar chart
        fig.add_trace(go.Bar(
            x=site_df_sorted["site_id"],
            y=site_df_sorted["performance_score"],
            name="Performance Score",
            marker_color=site_df_sorted["performance_score"],
            marker_colorscale="RdYlGn",
            text=site_df_sorted["performance_score"].round(1),
            textposition="outside"
        ))
        
        # Add threshold lines
        fig.add_hline(y=80, line_dash="dash", line_color="green", 
                     annotation_text="Target (80)")
        fig.add_hline(y=60, line_dash="dash", line_color="orange", 
                     annotation_text="Acceptable (60)")
        
        fig.update_layout(
            title="Site Performance Scores",
            xaxis_title="Site ID",
            yaxis_title="Performance Score",
            yaxis_range=[0, 110],
            showlegend=False
        )
        
        st.plotly_chart(fig, width='stretch')
    
    # Site details table
    st.write("**Complete Site Metrics**")
    display_cols = ["site_id", "subject_count", "total_missing_visits", "total_missing_pages", 
                   "total_open_queries", "performance_score"]
    display_cols = [col for col in display_cols if col in site_df.columns]
    
    # Add styling
    styled_site_df = site_df[display_cols].copy()
    st.dataframe(
        styled_site_df,
        width='stretch',
        hide_index=True,
        column_config={
            "performance_score": st.column_config.ProgressColumn(
                "Performance",
                format="%.1f",
                min_value=0,
                max_value=100,
            ),
        }
    )


def render_cra_query_management(subject_df, site_df):
    """Render query management and tracking"""
    st.subheader("📝 Query Management Dashboard")
    
    if "open_queries" not in subject_df.columns:
        st.info("Query data not available")
        return
    
    # Query summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_queries = int(subject_df["open_queries"].sum())
    subjects_with_queries = (subject_df["open_queries"] > 0).sum()
    avg_queries_per_subject = total_queries / len(subject_df) if len(subject_df) > 0 else 0
    max_queries = int(subject_df["open_queries"].max())
    
    with col1:
        st.metric("Total Open Queries", total_queries)
    with col2:
        st.metric("Subjects with Queries", subjects_with_queries)
    with col3:
        st.metric("Avg Queries/Subject", f"{avg_queries_per_subject:.1f}")
    with col4:
        st.metric("Max Queries (Single Subject)", max_queries)
    
    st.markdown("---")
    
    # Query burden by site
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Query Burden by Site**")
        if "site_id" in subject_df.columns or "Site ID" in subject_df.columns:
            site_col = "site_id" if "site_id" in subject_df.columns else "Site ID"
            query_by_site = subject_df.groupby(site_col)["open_queries"].sum().sort_values(ascending=False)
            
            fig = px.bar(
                x=query_by_site.index,
                y=query_by_site.values,
                labels={"x": "Site ID", "y": "Total Open Queries"},
                title="Query Burden Distribution"
            )
            st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.write("**Query Hotspots (Sites with High Query Load)**")
        if "site_id" in subject_df.columns or "Site ID" in subject_df.columns:
            site_col = "site_id" if "site_id" in subject_df.columns else "Site ID"
            query_hotspots = subject_df.groupby(site_col).agg({
                "open_queries": ["sum", "mean", "count"]
            }).round(2)
            query_hotspots.columns = ["Total Queries", "Avg per Subject", "Subject Count"]
            query_hotspots = query_hotspots.sort_values("Total Queries", ascending=False).head(10)
            st.dataframe(query_hotspots, use_container_width=True)
    
    # Subjects with high query burden
    st.write("**Subjects Requiring Immediate Attention (≥3 Open Queries)**")
    high_query_subjects = subject_df[subject_df["open_queries"] >= 3].copy()
    
    if not high_query_subjects.empty:
        display_cols = ["Subject ID", "Site ID", "site_id", "open_queries", "missing_visits", "missing_pages", "risk_level"]
        display_cols = [col for col in display_cols if col in high_query_subjects.columns]
        
        # Use first available
        if "Subject ID" not in display_cols and "subject_id" in high_query_subjects.columns:
            display_cols = ["subject_id"] + [c for c in display_cols if c != "Subject ID"]
        if "Site ID" not in display_cols and "site_id" in display_cols:
            display_cols = [c for c in display_cols if c != "Site ID"]
        
        high_query_subjects_sorted = high_query_subjects[display_cols].sort_values("open_queries", ascending=False)
        
        st.dataframe(
            high_query_subjects_sorted,
            width='stretch',
            hide_index=True
        )
        
        # Download button
        csv = high_query_subjects_sorted.to_csv(index=False)
        st.download_button(
            label="📥 Download Query Report",
            data=csv,
            file_name=f"high_query_subjects_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.success("✅ No subjects with high query burden")


def render_cra_visit_compliance(subject_df, site_df):
    """Render visit compliance monitoring"""
    st.subheader("📅 Visit Compliance Monitoring")
    
    if "missing_visits" not in subject_df.columns:
        st.info("Visit data not available")
        return
    
    # Visit compliance summary
    col1, col2, col3, col4 = st.columns(4)
    
    total_missing = int(subject_df["missing_visits"].sum())
    subjects_with_missing = (subject_df["missing_visits"] > 0).sum()
    compliance_rate = ((len(subject_df) - subjects_with_missing) / len(subject_df) * 100) if len(subject_df) > 0 else 100
    sites_with_missing = len(site_df[site_df["total_missing_visits"] > 0]) if "total_missing_visits" in site_df.columns else 0
    
    with col1:
        st.metric("Total Missing Visits", total_missing, delta="Alert" if total_missing > 20 else None)
    with col2:
        st.metric("Subjects Affected", subjects_with_missing)
    with col3:
        st.metric("Visit Compliance Rate", f"{compliance_rate:.1f}%")
    with col4:
        st.metric("Sites with Missing Visits", sites_with_missing)
    
    st.markdown("---")
    
    # Visit compliance visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Missing Visits by Site**")
        if "total_missing_visits" in site_df.columns:
            sites_with_issues = site_df[site_df["total_missing_visits"] > 0].sort_values("total_missing_visits", ascending=False)
            
            if not sites_with_issues.empty:
                fig = px.bar(
                    sites_with_issues.head(15),
                    x="site_id",
                    y="total_missing_visits",
                    title="Top 15 Sites by Missing Visits",
                    labels={"total_missing_visits": "Missing Visits", "site_id": "Site ID"}
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.success("✅ No missing visits across all sites")
    
    with col2:
        st.write("**Missing Visits Distribution**")
        visit_dist = subject_df["missing_visits"].value_counts().sort_index()
        
        fig = px.bar(
            x=visit_dist.index,
            y=visit_dist.values,
            labels={"x": "Number of Missing Visits", "y": "Subject Count"},
            title="Distribution of Missing Visits per Subject"
        )
        st.plotly_chart(fig, width='stretch')
    
    # Data completeness by site
    st.write("**Data Completeness Overview by Site**")
    if "total_missing_pages" in site_df.columns:
        completeness_df = site_df[["site_id", "subject_count", "total_missing_visits", "total_missing_pages"]].copy()
        completeness_df = completeness_df.sort_values("total_missing_visits", ascending=False)
        
        st.dataframe(
            completeness_df,
            width='stretch',
            hide_index=True,
            column_config={
                "total_missing_visits": st.column_config.NumberColumn(
                    "Missing Visits",
                    help="Total missing visits at this site",
                    format="%d 🚨" if completeness_df["total_missing_visits"].max() > 0 else "%d",
                ),
                "total_missing_pages": st.column_config.NumberColumn(
                    "Missing Pages",
                    help="Total missing pages at this site",
                    format="%d",
                ),
            }
        )
    
    # Critical subjects list
    st.write("**Subjects with Multiple Missing Visits (Requires Follow-up)**")
    critical_subjects = subject_df[subject_df["missing_visits"] >= 2].copy()
    
    if not critical_subjects.empty:
        display_cols = []
        for col in ["subject_id", "Subject ID", "site_id", "Site ID", "missing_visits", "missing_pages", "open_queries"]:
            if col in critical_subjects.columns and col not in display_cols:
                display_cols.append(col)
        
        critical_subjects_sorted = critical_subjects[display_cols].sort_values("missing_visits", ascending=False)
        
        st.dataframe(
            critical_subjects_sorted,
            width='stretch',
            hide_index=True
        )
    else:
        st.success("✅ No subjects with multiple missing visits")


def render_cra_action_items(subject_df, site_df, study_metrics, risk_engine, study_name):
    """Render CRA action items and recommendations"""
    st.subheader("⚠️ Action Items & Recommendations")
    
    # Priority sites for monitoring visits
    st.write("### 🎯 Priority Sites for Monitoring Visits")
    
    if "performance_score" in site_df.columns:
        # Calculate urgency score for each site
        site_priorities = site_df.copy()
        
        # Urgency calculation
        site_priorities["urgency_score"] = (
            site_priorities.get("total_missing_visits", 0) * 5 +
            site_priorities.get("total_open_queries", 0) * 2 +
            (100 - site_priorities.get("performance_score", 100))
        )
        
        site_priorities = site_priorities.sort_values("urgency_score", ascending=False)
        
        # Top 10 priority sites
        priority_sites = site_priorities.head(10)
        
        display_cols = ["site_id", "subject_count", "total_missing_visits", "total_open_queries", 
                       "performance_score", "urgency_score"]
        display_cols = [col for col in display_cols if col in priority_sites.columns]
        
        st.dataframe(
            priority_sites[display_cols],
            width='stretch',
            hide_index=True,
            column_config={
                "urgency_score": st.column_config.NumberColumn(
                    "Urgency Score",
                    help="Higher score = more urgent",
                    format="%.0f 🔴",
                ),
                "performance_score": st.column_config.ProgressColumn(
                    "Performance",
                    format="%.1f",
                    min_value=0,
                    max_value=100,
                ),
            }
        )
    
    st.markdown("---")
    
    # Action items by category
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 📝 Query Resolution Actions")
        
        # Sites needing query resolution
        if "total_open_queries" in site_df.columns:
            high_query_sites = site_df[site_df["total_open_queries"] >= 10].sort_values("total_open_queries", ascending=False)
            
            if not high_query_sites.empty:
                for idx, site in high_query_sites.head(5).iterrows():
                    with st.expander(f"🏥 Site {site['site_id']} - {int(site['total_open_queries'])} queries"):
                        st.write(f"**Priority:** High")
                        st.write(f"**Subject Count:** {int(site.get('subject_count', 0))}")
                        st.write(f"**Action:** Schedule query resolution session")
                        st.write(f"**Timeline:** Within 1 week")
                        st.write(f"**Impact:** Database lock timeline at risk")
            else:
                st.success("✅ No sites with high query burden")
    
    with col2:
        st.write("### 📅 Visit Compliance Actions")
        
        # Sites needing visit follow-up
        if "total_missing_visits" in site_df.columns:
            missing_visit_sites = site_df[site_df["total_missing_visits"] >= 5].sort_values("total_missing_visits", ascending=False)
            
            if not missing_visit_sites.empty:
                for idx, site in missing_visit_sites.head(5).iterrows():
                    with st.expander(f"🏥 Site {site['site_id']} - {int(site['total_missing_visits'])} missing visits"):
                        st.write(f"**Priority:** High")
                        st.write(f"**Subject Count:** {int(site.get('subject_count', 0))}")
                        st.write(f"**Action:** Contact site coordinator to schedule overdue visits")
                        st.write(f"**Timeline:** Immediate")
                        st.write(f"**Impact:** Data completeness at risk")
            else:
                st.success("✅ No sites with significant missing visits")
    
    # High-risk subjects requiring attention
    st.write("### 🚨 High-Risk Subjects Requiring Attention")
    
    if "risk_level" in subject_df.columns:
        high_risk = subject_df[subject_df["risk_level"] == "High"].copy()
        
        if not high_risk.empty:
            # Get columns that exist
            display_cols = []
            for col in ["subject_id", "Subject ID", "site_id", "Site ID", "dqi_score", 
                       "open_queries", "missing_visits", "missing_pages"]:
                if col in high_risk.columns:
                    display_cols.append(col)
            
            high_risk_sorted = high_risk[display_cols].sort_values(
                "dqi_score" if "dqi_score" in display_cols else display_cols[0]
            ).head(15)
            
            st.dataframe(
                high_risk_sorted,
                width='stretch',
                hide_index=True
            )
            
            st.warning(f"⚠️ {len(high_risk)} high-risk subjects identified. Review and address data quality issues.")
        else:
            st.success("✅ No high-risk subjects identified")
    
    # Download action items report
    st.markdown("---")
    st.write("### 📥 Export Action Items")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export Priority Sites"):
            if "urgency_score" in site_priorities.columns:
                csv = site_priorities.head(20).to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"priority_sites_{study_name}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    with col2:
        if st.button("Export High-Risk Subjects"):
            if "risk_level" in subject_df.columns:
                high_risk_export = subject_df[subject_df["risk_level"] == "High"]
                if not high_risk_export.empty:
                    csv = high_risk_export.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"high_risk_subjects_{study_name}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
    
    with col3:
        if st.button("Export Complete Report"):
            # Create comprehensive report
            report_data = {
                "Study": study_name,
                "Total Sites": len(site_df),
                "Total Subjects": len(subject_df),
                "Open Queries": int(subject_df["open_queries"].sum()) if "open_queries" in subject_df.columns else 0,
                "Missing Visits": int(subject_df["missing_visits"].sum()) if "missing_visits" in subject_df.columns else 0,
                "High Risk Subjects": (subject_df["risk_level"] == "High").sum() if "risk_level" in subject_df.columns else 0,
            }
            
            report_df = pd.DataFrame([report_data])
            csv = report_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"cra_summary_{study_name}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )


def render_cra_analytics(subject_df, site_df, study_metrics):
    """Render advanced analytics for CRA"""
    st.subheader("📊 Advanced Analytics")
    
    # Correlation analysis
    st.write("### 📈 Performance Correlation Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Query vs. Performance Relationship**")
        if all(col in site_df.columns for col in ["total_open_queries", "performance_score"]):
            fig = px.scatter(
                site_df,
                x="total_open_queries",
                y="performance_score",
                size="subject_count",
                hover_data=["site_id"],
                title="Site Performance vs Query Burden",
                labels={"total_open_queries": "Total Open Queries", "performance_score": "Performance Score"}
            )
            st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.write("**Missing Visits vs. Performance**")
        if all(col in site_df.columns for col in ["total_missing_visits", "performance_score"]):
            fig = px.scatter(
                site_df,
                x="total_missing_visits",
                y="performance_score",
                size="subject_count",
                hover_data=["site_id"],
                title="Site Performance vs Missing Visits",
                labels={"total_missing_visits": "Total Missing Visits", "performance_score": "Performance Score"}
            )
            st.plotly_chart(fig, width='stretch')
    
    # Subject count distribution
    st.write("### 📊 Site Enrollment Distribution")
    
    if "subject_count" in site_df.columns:
        fig = px.histogram(
            site_df,
            x="subject_count",
            title="Distribution of Subjects per Site",
            labels={"subject_count": "Number of Subjects"},
            nbins=15
        )
        st.plotly_chart(fig, width='stretch')
    
    # Performance trends
    st.write("### 📉 Performance Metrics Summary")
    
    if "performance_score" in site_df.columns:
        perf_stats = {
            "Metric": ["Mean Performance", "Median Performance", "Min Performance", "Max Performance", "Std Dev"],
            "Value": [
                f"{site_df['performance_score'].mean():.1f}",
                f"{site_df['performance_score'].median():.1f}",
                f"{site_df['performance_score'].min():.1f}",
                f"{site_df['performance_score'].max():.1f}",
                f"{site_df['performance_score'].std():.1f}"
            ]
        }
        
        perf_stats_df = pd.DataFrame(perf_stats)
        st.dataframe(perf_stats_df, width='stretch', hide_index=True)
    
    # Site ranking
    st.write("### 🏆 Site Performance Ranking")
    
    if "performance_score" in site_df.columns:
        ranked_sites = site_df.sort_values("performance_score", ascending=False).reset_index(drop=True)
        ranked_sites.index = ranked_sites.index + 1
        ranked_sites.index.name = "Rank"
        
        display_cols = ["site_id", "subject_count", "performance_score", "total_open_queries", "total_missing_visits"]
        display_cols = [col for col in display_cols if col in ranked_sites.columns]
        
        st.dataframe(
            ranked_sites[display_cols],
            width='stretch',
            column_config={
                "performance_score": st.column_config.ProgressColumn(
                    "Performance",
                    format="%.1f",
                    min_value=0,
                    max_value=100,
                ),
            }
        )


def render_ai_insights_page(all_data, all_metrics, risk_engine):
    """Render dedicated AI Insights page with actionable recommendations"""
    st.header("🤖 AI-Powered Actionable Insights")
    st.markdown("*Powered by Google Gemini AI*")
    
    if not all_metrics:
        st.info("📤 No data loaded yet. Go to **'Upload & Analyze'** to upload your study files and view them here!")
        return
    
    # Initialize Generative AI
    gen_ai = GenerativeAI()
    
    # Tabs for different insight types
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Executive Summary",
        "⚠️ Critical Actions",
        "📊 Study-Level Insights",
        "🔍 Deep Dive Analysis",
        "💬 Ask AI"
    ])
    
    with tab1:
        st.subheader("Executive Portfolio Summary")
        
        if st.button("Generate Portfolio Summary", key="exec_summary"):
            with st.spinner("Analyzing entire portfolio with Gemini AI..."):
                narrative = gen_ai.generate_executive_dashboard_narrative(all_metrics)
                st.success("✅ Analysis Complete")
                st.markdown(f"### Portfolio Overview\n\n{narrative}")
        
        # Key Portfolio Metrics
        st.markdown("---")
        st.subheader("Portfolio Metrics at a Glance")
        
        total_studies = len(all_metrics)
        total_subjects = sum(m.get("subject_metrics", pd.DataFrame()).shape[0] for m in all_metrics.values())
        total_sites = sum(len(m.get("site_metrics", [])) for m in all_metrics.values())
        
        # Calculate average DQI across all subjects
        all_dqi_scores = []
        for m in all_metrics.values():
            if "subject_metrics" in m and "dqi_score" in m["subject_metrics"].columns:
                all_dqi_scores.extend(m["subject_metrics"]["dqi_score"].dropna().tolist())
        avg_dqi = sum(all_dqi_scores) / len(all_dqi_scores) if all_dqi_scores else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Studies", total_studies)
        with col2:
            st.metric("Total Subjects", total_subjects)
        with col3:
            st.metric("Total Sites", total_sites)
        with col4:
            st.metric("Avg DQI Score", f"{avg_dqi:.1f}")
    
    with tab2:
        st.subheader("⚠️ Critical Actions Required")
        st.markdown("*Top priority items requiring immediate attention*")
        
        # Collect high-risk entities across all studies
        critical_actions = []
        
        for study_name, metrics in all_metrics.items():
            if "subject_metrics" in metrics:
                subject_df = metrics["subject_metrics"]
                high_risk = subject_df[subject_df["risk_level"] == "High"] if "risk_level" in subject_df.columns else pd.DataFrame()
                
                if not high_risk.empty:
                    for _, row in high_risk.head(5).iterrows():
                        critical_actions.append({
                            "study": study_name,
                            "subject": row.get("subject_id", "N/A"),
                            "site": row.get("site_id", "N/A"),
                            "dqi": row.get("dqi", 0),
                            "issues": row.get("open_queries", 0)
                        })
        
        if critical_actions:
            st.warning(f"🚨 Found {len(critical_actions)} high-risk items requiring immediate action")
            
            if st.button("Generate Action Plan", key="action_plan"):
                with st.spinner("Generating prioritized action plan with Gemini AI..."):
                    # Build context for AI
                    context = "High-Risk Items:\n"
                    for action in critical_actions[:10]:  # Top 10
                        context += f"- Study {action['study']}, Subject {action['subject']}, Site {action['site']}: DQI={action['dqi']:.1f}, Issues={action['issues']}\n"
                    
                    prompt = f"""Analyze these high-risk clinical trial subjects and provide:
1. Top 3 most urgent actions (be specific)
2. Resource allocation recommendations
3. Timeline for resolution (realistic estimates)

{context}

Provide actionable, prioritized recommendations."""
                    
                    system_message = "You are a clinical operations director creating action plans for quality improvement."
                    action_plan = gen_ai._generate_completion(prompt, system_message)
                    
                    st.success("✅ Action Plan Generated")
                    st.markdown(f"### Recommended Actions\n\n{action_plan}")
            
            # Display critical items table
            st.markdown("---")
            st.subheader("Critical Items Detail")
            critical_df = pd.DataFrame(critical_actions)
            st.dataframe(critical_df, use_container_width=True)
        else:
            st.success("✅ No critical high-risk items found. Portfolio is performing well!")
    
    with tab3:
        st.subheader("📊 Study-Level Insights")
        
        # Select study
        study_names = list(all_metrics.keys())
        selected_study = st.selectbox("Select Study for AI Analysis", study_names, key="ai_study_select")
        
        if selected_study and selected_study in all_metrics:
            study_metrics = all_metrics[selected_study]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                if st.button("Generate Study Analysis", key="study_analysis"):
                    with st.spinner("Analyzing study with Gemini AI..."):
                        summary = gen_ai.summarize_study_performance(selected_study, study_metrics)
                        st.success("✅ Analysis Complete")
                        st.markdown(f"### Study Analysis\n\n{summary}")
                        
                        # Additional insights
                        st.markdown("---")
                        if st.button("Get Detailed Recommendations", key="detailed_recs"):
                            with st.spinner("Generating detailed recommendations..."):
                                # Calculate metrics from subject_metrics
                                subject_df = study_metrics.get("subject_metrics", pd.DataFrame())
                                total_subj = len(subject_df)
                                if not subject_df.empty:
                                    clean_rt = (subject_df["is_clean_patient"].sum() / len(subject_df) * 100) if "is_clean_patient" in subject_df.columns else 0
                                    avg_dqi_val = subject_df["dqi_score"].mean() if "dqi_score" in subject_df.columns else 0
                                    open_q = subject_df["open_queries"].sum() if "open_queries" in subject_df.columns else 0
                                else:
                                    clean_rt = 0
                                    avg_dqi_val = 0
                                    open_q = 0
                                
                                prompt = f"""Based on this study's performance:
- Total Subjects: {total_subj}
- Clean Rate: {clean_rt:.1f}%
- Open Queries: {open_q}
- Avg DQI: {avg_dqi_val:.1f}

Provide:
1. 3 specific improvement actions
2. Expected impact of each action
3. Implementation difficulty (Low/Medium/High)
4. Estimated timeline for each

Be specific and actionable."""
                                
                                recommendations = gen_ai._generate_completion(
                                    prompt,
                                    "You are a clinical trial quality improvement consultant."
                                )
                                st.markdown(f"### Detailed Recommendations\n\n{recommendations}")
            
            with col2:
                # Calculate metrics from subject_metrics DataFrame
                subject_df = study_metrics.get("subject_metrics", pd.DataFrame())
                total_subjects = len(subject_df)
                
                if not subject_df.empty:
                    clean_rate = (subject_df["is_clean_patient"].sum() / len(subject_df) * 100) if "is_clean_patient" in subject_df.columns else 0
                    avg_dqi = subject_df["dqi_score"].mean() if "dqi_score" in subject_df.columns else 0
                else:
                    clean_rate = 0
                    avg_dqi = 0
                
                st.metric("Total Subjects", total_subjects)
                st.metric("Clean Rate", f"{clean_rate:.1f}%")
                st.metric("Avg DQI", f"{avg_dqi:.1f}")
    
    with tab4:
        st.subheader("🔍 Deep Dive Analysis")
        st.markdown("*Advanced AI-powered analysis of specific issues*")
        
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Query Hotspot Analysis", "Site Performance Patterns", "Data Completeness Trends", "Risk Factor Correlation"]
        )
        
        if st.button("Run Deep Dive Analysis", key="deep_dive"):
            with st.spinner(f"Running {analysis_type} with Gemini AI..."):
                # Collect relevant data based on analysis type
                if analysis_type == "Query Hotspot Analysis":
                    total_queries = sum(m.get("total_open_queries", 0) for m in all_metrics.values())
                    context = f"Total open queries across portfolio: {total_queries}\n"
                    
                    prompt = f"""{context}\nAnalyze query patterns and identify:
1. Root causes of high query volumes
2. Which studies/sites need training
3. Process improvements to reduce queries
4. Expected reduction targets"""
                
                elif analysis_type == "Site Performance Patterns":
                    prompt = f"""Analyze site performance across {len(all_metrics)} studies.
Identify:
1. Common characteristics of top-performing sites
2. Red flags in underperforming sites
3. Actionable interventions for improvement
4. Best practices to replicate"""
                
                elif analysis_type == "Data Completeness Trends":
                    avg_completeness = sum(m.get("avg_completeness", 0) for m in all_metrics.values()) / len(all_metrics) if all_metrics else 0
                    prompt = f"""Portfolio average completeness: {avg_completeness:.1f}%\n
Provide:
1. Assessment of completeness status
2. Target completeness rate
3. Actions to improve completeness
4. Timeline to reach target"""
                
                else:  # Risk Factor Correlation
                    prompt = """Analyze correlation between risk factors:
- Missing pages vs query volumes
- Site size vs data quality
- Study phase vs completion rates

Provide actionable insights on which factors to prioritize."""
                
                analysis = gen_ai._generate_completion(
                    prompt,
                    "You are a data scientist analyzing clinical trial operational data."
                )
                
                st.success("✅ Deep Dive Complete")
                st.markdown(f"### {analysis_type}\n\n{analysis}")
    
    with tab5:
        st.subheader("💬 Ask AI About Your Data")
        st.markdown("*Ask any question about your clinical trial data - Gemini AI will analyze and respond*")
        
        # Custom question input
        user_question = st.text_area(
            "Your Question",
            placeholder="Example: Which studies are at risk of missing database lock deadlines?",
            height=100
        )
        
        if st.button("Ask Gemini AI", key="ask_ai"):
            if user_question:
                with st.spinner("Analyzing your question with Gemini AI..."):
                    # Build context from all available data
                    context_data = {
                        "total_studies": len(all_metrics),
                        "total_subjects": sum(m.get("total_subjects", 0) for m in all_metrics.values()),
                        "study_names": list(all_metrics.keys()),
                        "avg_dqi": sum(m.get("avg_dqi", 0) for m in all_metrics.values()) / len(all_metrics) if all_metrics else 0,
                        "total_queries": sum(m.get("total_open_queries", 0) for m in all_metrics.values())
                    }
                    
                    answer = gen_ai.answer_natural_language_query(user_question, context_data)
                    
                    st.success("✅ Answer Generated")
                    st.markdown(f"### Answer\n\n{answer}")
            else:
                st.warning("Please enter a question.")
        
        # Example questions
        st.markdown("---")
        st.markdown("**Example Questions:**")
        examples = [
            "Which sites are consistently underperforming?",
            "What are the main drivers of poor data quality?",
            "How can we improve our clean data rate?",
            "Which studies need immediate CRA attention?",
            "What's causing the high query volumes?"
        ]
        for example in examples:
            st.markdown(f"- {example}")


def render_upload_analyze(active_tab=None):
    """Render upload and analyze page for custom data"""
    st.header("📤 Upload & Analyze Your Data")
    st.markdown("Upload your clinical trial data files and get instant insights powered by AI")
    st.markdown("---")
    
    # Instructions
    with st.expander("📋 Upload Instructions", expanded=True):
        st.markdown("""
        **Supported File Types:**
        - Global Missing Pages Report (Excel)
        - Visit Projection Tracker (Excel)
        - Compiled EDRR (Excel)
        - SAE Dashboard (Excel)
        - Coding Reports - MedDRA & WHODrug (Excel)
        
        **How to Upload:**
        1. Enter a name for your study
        2. Upload one or more Excel files from your study
        3. Click "Analyze Data" to process
        4. View comprehensive insights across multiple tabs
        
        **File Format:**
        - Files should follow standard clinical trial report formats
        - Multi-row headers are supported
        - Subject ID, Site ID columns will be auto-detected
        """)
    
    # Study name input
    study_name = st.text_input("Study Name", placeholder="e.g., Study ABC-123", help="Give your study a unique name")
    
    # File upload
    st.subheader("📁 Upload Data Files")
    uploaded_files = st.file_uploader(
        "Upload Excel files (you can select multiple files)",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        help="Upload all available Excel reports for comprehensive analysis"
    )
    
    # Initialize session state for uploaded data
    if 'uploaded_study_name' not in st.session_state:
        st.session_state.uploaded_study_name = None
    if 'uploaded_study_df' not in st.session_state:
        st.session_state.uploaded_study_df = None
    if 'uploaded_study_metrics' not in st.session_state:
        st.session_state.uploaded_study_metrics = None
    if 'uploaded_all_metrics' not in st.session_state:
        st.session_state.uploaded_all_metrics = None
    if 'uploaded_canonical_entities' not in st.session_state:
        st.session_state.uploaded_canonical_entities = None
    if 'uploaded_risk_engine' not in st.session_state:
        st.session_state.uploaded_risk_engine = None
    
    if uploaded_files and study_name:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded for {study_name}")
        
        # Show uploaded files
        with st.expander("📄 Uploaded Files"):
            for i, file in enumerate(uploaded_files, 1):
                st.write(f"{i}. {file.name} ({file.size / 1024:.1f} KB)")
        
        # Analyze button
        if st.button("🔍 Analyze Data", type="primary", key="analyze_uploaded_data"):
            with st.spinner(f"Processing {study_name}..."):
                try:
                    # Process uploaded files
                    from ingestion.multi_file_loader import MultiFileDataLoader
                    from harmonization import CanonicalDataModel
                    from metrics import MetricsEngine, DataQualityIndex
                    from intelligence import RiskIntelligence
                    import tempfile
                    import os
                    
                    # Create temp directory for uploaded files
                    with tempfile.TemporaryDirectory() as temp_dir:
                        study_dir = os.path.join(temp_dir, study_name)
                        os.makedirs(study_dir, exist_ok=True)
                        
                        # Save uploaded files to temp directory
                        for uploaded_file in uploaded_files:
                            file_path = os.path.join(study_dir, uploaded_file.name)
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                        
                        # Load data using MultiFileDataLoader
                        loader = MultiFileDataLoader(temp_dir)
                        study_df = loader.load_study_data(study_name)
                        
                        if study_df is not None and not study_df.empty:
                            st.success(f"✅ Successfully loaded {len(study_df)} subjects from {study_name}")
                            
                            # Build canonical model
                            all_data = {study_name: study_df}
                            canonical_model = CanonicalDataModel()
                            canonical_entities = canonical_model.build_canonical_model(all_data)
                            
                            # Calculate metrics
                            metrics_engine = MetricsEngine(canonical_entities, all_data)
                            study_metrics = metrics_engine.calculate_all_metrics_for_study(study_name)
                            
                            # Calculate DQI
                            dqi_calculator = DataQualityIndex()
                            if "subject_metrics" in study_metrics:
                                study_metrics["subject_metrics"] = dqi_calculator.calculate_subject_dqi(
                                    study_metrics["subject_metrics"]
                                )
                            
                            all_metrics = {study_name: study_metrics}
                            
                            # Risk intelligence
                            risk_engine = RiskIntelligence(all_metrics)
                            
                            # Store in session state
                            st.session_state.uploaded_study_name = study_name
                            st.session_state.uploaded_study_df = study_df
                            st.session_state.uploaded_study_metrics = study_metrics
                            st.session_state.uploaded_all_metrics = all_metrics
                            st.session_state.uploaded_canonical_entities = canonical_entities
                            st.session_state.uploaded_risk_engine = risk_engine
                            
                        else:
                            st.error("❌ Failed to load data. Please check your file formats.")
                
                except Exception as e:
                    st.error(f"❌ Error processing data: {str(e)}")
                    st.exception(e)
        
        # Display results if data has been analyzed
        if st.session_state.uploaded_study_name == study_name and st.session_state.uploaded_study_metrics is not None:
            study_df = st.session_state.uploaded_study_df
            study_metrics = st.session_state.uploaded_study_metrics
            all_metrics = st.session_state.uploaded_all_metrics
            canonical_entities = st.session_state.uploaded_canonical_entities
            risk_engine = st.session_state.uploaded_risk_engine
            
            st.markdown("---")
            
            # Use tab from sidebar, default to Overview if not set
            if active_tab is None:
                active_tab = "📊 Overview"
            
            if active_tab == "📊 Overview":
                render_uploaded_data_overview(study_name, study_metrics, canonical_entities)
            
            elif active_tab == "🏥 Site Performance":
                if "site_metrics" in study_metrics and "subject_metrics" in study_metrics:
                    render_cra_site_performance(
                        study_metrics["site_metrics"],
                        study_metrics["subject_metrics"],
                        study_df
                    )
                else:
                    st.info("Site metrics not available")
            
            elif active_tab == "📝 Query Management":
                if "subject_metrics" in study_metrics and "site_metrics" in study_metrics:
                    render_cra_query_management(
                        study_metrics["subject_metrics"],
                        study_metrics["site_metrics"]
                    )
                else:
                    st.info("Query metrics not available")
            
            elif active_tab == "⚠️ Action Items":
                if "subject_metrics" in study_metrics and "site_metrics" in study_metrics:
                    render_cra_action_items(
                        study_metrics["subject_metrics"],
                        study_metrics["site_metrics"],
                        study_metrics,
                        risk_engine,
                        study_name
                    )
                else:
                    st.info("Action items not available")
            
            # AI-Powered Insights Tabs
            elif active_tab == "📋 Executive Summary":
                render_uploaded_executive_summary(study_name, all_metrics)
            
            elif active_tab == "⚠️ Critical Actions":
                render_uploaded_critical_actions(study_name, all_metrics)
            
            elif active_tab == "📊 Study-Level Insights":
                render_uploaded_study_insights(study_name, study_metrics)
            
            elif active_tab == "🔍 Deep Dive Analysis":
                render_uploaded_deep_dive(study_name, all_metrics)
            
            elif active_tab == "💬 Ask AI":
                render_uploaded_ask_ai(study_name, study_metrics, study_df)
    
    elif uploaded_files and not study_name:
        st.warning("⚠️ Please enter a study name to continue")
    
    elif not uploaded_files:
        st.info("👆 Upload your data files to get started")
        
        # Sample data format guide
        with st.expander("📖 Sample Data Format Guide"):
            st.markdown("""
            **Expected File Names (any of these):**
            - `*Missing_Pages*` - Missing pages report
            - `*Visit Projection*` or `*Visit_Tracker*` - Visit tracking
            - `*EDRR*` - Query/issue tracking
            - `*SAE*` or `*Safety*` - Safety events
            - `*MedDRA*` or `*WHODrug*` or `*Coding*` - Coding reports
            
            **Key Columns to Include:**
            - Subject ID (variations accepted: Subject, Participant, Patient ID, etc.)
            - Site ID (variations accepted: Site, Center, Investigator Site, etc.)
            - Visit information, query counts, missing data indicators
            
            **Tips:**
            - Include as many file types as possible for comprehensive analysis
            - Files will be automatically matched to the correct report type
            - Multi-row headers are automatically handled
            - Column names are standardized during processing
            """)


def render_uploaded_data_overview(study_name, study_metrics, canonical_entities):
    """Render overview of uploaded data analysis"""
    st.subheader(f"📊 Analysis Overview: {study_name}")
    
    if "subject_metrics" in study_metrics:
        subject_df = study_metrics["subject_metrics"]
        site_df = study_metrics.get("site_metrics", pd.DataFrame())
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Subjects", len(subject_df))
        
        with col2:
            total_sites = len(site_df) if not site_df.empty else len(subject_df["site_id"].unique()) if "site_id" in subject_df.columns else 0
            st.metric("Total Sites", total_sites)
        
        with col3:
            avg_dqi = subject_df["dqi_score"].mean() if "dqi_score" in subject_df.columns else 0
            st.metric("Average DQI", f"{avg_dqi:.1f}")
        
        with col4:
            clean_count = subject_df["is_clean_patient"].sum() if "is_clean_patient" in subject_df.columns else 0
            clean_pct = (clean_count / len(subject_df) * 100) if len(subject_df) > 0 else 0
            st.metric("Clean Data Rate", f"{clean_pct:.1f}%")
        
        st.markdown("---")
        
        # Key findings
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### 📈 Key Metrics")
            
            total_queries = int(subject_df["open_queries"].sum()) if "open_queries" in subject_df.columns else 0
            total_missing_visits = int(subject_df["missing_visits"].sum()) if "missing_visits" in subject_df.columns else 0
            total_missing_pages = int(subject_df["missing_pages"].sum()) if "missing_pages" in subject_df.columns else 0
            
            metrics_data = {
                "Metric": ["Open Queries", "Missing Visits", "Missing Pages", "Clean Subjects"],
                "Value": [
                    total_queries,
                    total_missing_visits,
                    total_missing_pages,
                    clean_count
                ]
            }
            
            st.dataframe(pd.DataFrame(metrics_data), hide_index=True, width='stretch')
        
        with col2:
            st.write("### ⚠️ Risk Distribution")
            
            if "risk_level" in subject_df.columns:
                risk_counts = subject_df["risk_level"].value_counts()
                
                fig = px.pie(
                    values=risk_counts.values,
                    names=risk_counts.index,
                    title="Subject Risk Levels",
                    color_discrete_map={"High": "#d62728", "Medium": "#ff7f0e", "Low": "#2ca02c"}
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("Risk assessment not available")
        
        # DQI distribution
        st.write("### 📊 Data Quality Distribution")
        
        if "dqi_score" in subject_df.columns:
            fig = px.histogram(
                subject_df,
                x="dqi_score",
                nbins=20,
                title="DQI Score Distribution",
                labels={"dqi_score": "DQI Score"},
                color_discrete_sequence=["#1f77b4"]
            )
            fig.add_vline(x=avg_dqi, line_dash="dash", line_color="red", annotation_text=f"Mean: {avg_dqi:.1f}")
            st.plotly_chart(fig, width='stretch')
        
        # Export option
        st.markdown("---")
        st.write("### 📥 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export Subject Metrics"):
                csv = subject_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{study_name}_subject_metrics_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if not site_df.empty and st.button("Export Site Metrics"):
                csv = site_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{study_name}_site_metrics_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )


def render_uploaded_executive_summary(study_name, all_metrics):
    """Render AI-powered executive summary for uploaded data"""
    st.subheader("📋 Executive Summary")
    st.markdown("*AI-generated insights powered by Google Gemini*")
    
    gen_ai = GenerativeAI()
    
    # Initialize session state for this summary
    if 'uploaded_exec_summary' not in st.session_state:
        st.session_state.uploaded_exec_summary = None
    
    if st.button("📋 Generate Executive Summary", key="upload_exec_summary", type="primary"):
        with st.spinner("Analyzing your study with Gemini AI..."):
            narrative = gen_ai.generate_executive_dashboard_narrative(all_metrics)
            st.session_state.uploaded_exec_summary = narrative
    
    # Display the summary if it exists
    if st.session_state.uploaded_exec_summary:
        st.success("✅ Analysis Complete")
        st.markdown(f"### Study Overview\n\n{st.session_state.uploaded_exec_summary}")
    
    # Key metrics display
    st.markdown("---")
    st.subheader("Key Metrics at a Glance")
    
    study_metrics = all_metrics.get(study_name, {})
    subject_df = study_metrics.get("subject_metrics", pd.DataFrame())
    
    if not subject_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Subjects", len(subject_df))
        
        with col2:
            clean_count = subject_df["is_clean_patient"].sum() if "is_clean_patient" in subject_df.columns else 0
            clean_pct = (clean_count / len(subject_df) * 100) if len(subject_df) > 0 else 0
            st.metric("Clean Data Rate", f"{clean_pct:.1f}%")
        
        with col3:
            avg_dqi = subject_df["dqi_score"].mean() if "dqi_score" in subject_df.columns else 0
            st.metric("Average DQI", f"{avg_dqi:.1f}")
        
        with col4:
            high_risk = (subject_df["risk_level"] == "High").sum() if "risk_level" in subject_df.columns else 0
            st.metric("High Risk Subjects", high_risk)


def render_uploaded_critical_actions(study_name, all_metrics):
    """Render critical actions for uploaded data"""
    st.subheader("⚠️ Critical Actions Required")
    st.markdown("*AI-prioritized action items*")
    
    gen_ai = GenerativeAI()
    study_metrics = all_metrics.get(study_name, {})
    subject_df = study_metrics.get("subject_metrics", pd.DataFrame())
    
    if not subject_df.empty and "risk_level" in subject_df.columns:
        high_risk = subject_df[subject_df["risk_level"] == "High"]
        
        if not high_risk.empty:
            st.warning(f"🚨 Found {len(high_risk)} high-risk items requiring immediate attention")
            
            # Show top high-risk subjects
            st.write("### Top High-Risk Subjects")
            display_cols = ["subject_id", "site_id", "dqi_score", "open_queries", "missing_visits", "missing_pages"]
            available_cols = [col for col in display_cols if col in high_risk.columns]
            st.dataframe(high_risk[available_cols].head(10), width='stretch')
            
            if st.button("Generate Action Plan", key="upload_action_plan"):
                with st.spinner("Generating prioritized action plan with Gemini AI..."):
                    context = f"High-Risk Items in {study_name}:\n"
                    for _, row in high_risk.head(10).iterrows():
                        context += f"- Subject {row.get('subject_id', 'N/A')}, Site {row.get('site_id', 'N/A')}: DQI={row.get('dqi_score', 0):.1f}, Issues={row.get('open_queries', 0)}\n"
                    
                    prompt = f"""{context}

Generate a prioritized action plan:
1. Immediate actions (next 24-48 hours)
2. Short-term actions (this week)
3. Medium-term improvements (this month)

For each action, specify:
- What to do
- Why it matters
- Who should do it
- Expected impact"""
                    
                    action_plan = gen_ai._generate_completion(
                        prompt,
                        "You are a clinical trial quality improvement consultant."
                    )
                    st.markdown(f"### Prioritized Action Plan\n\n{action_plan}")
        else:
            st.success("✅ No critical high-risk items found. Your study is performing well!")
    else:
        st.info("Risk assessment data not available")


def render_uploaded_study_insights(study_name, study_metrics):
    """Render AI study insights for uploaded data"""
    st.subheader("📊 Study-Level Insights")
    
    gen_ai = GenerativeAI()
    subject_df = study_metrics.get("subject_metrics", pd.DataFrame())
    
    if not subject_df.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("Generate Study Analysis", key="upload_study_analysis"):
                with st.spinner("Analyzing study with Gemini AI..."):
                    summary = gen_ai.summarize_study_performance(study_name, study_metrics)
                    st.success("✅ Analysis Complete")
                    st.markdown(f"### Study Analysis\n\n{summary}")
                    
                    st.markdown("---")
                    if st.button("Get Detailed Recommendations", key="upload_detailed_recs"):
                        with st.spinner("Generating detailed recommendations..."):
                            total_subj = len(subject_df)
                            clean_rt = (subject_df["is_clean_patient"].sum() / len(subject_df) * 100) if "is_clean_patient" in subject_df.columns else 0
                            avg_dqi_val = subject_df["dqi_score"].mean() if "dqi_score" in subject_df.columns else 0
                            open_q = subject_df["open_queries"].sum() if "open_queries" in subject_df.columns else 0
                            
                            prompt = f"""Based on this study's performance:
- Total Subjects: {total_subj}
- Clean Rate: {clean_rt:.1f}%
- Open Queries: {open_q}
- Avg DQI: {avg_dqi_val:.1f}

Provide:
1. 3 specific improvement actions
2. Expected impact of each action
3. Implementation difficulty (Low/Medium/High)
4. Estimated timeline for each

Be specific and actionable."""
                            
                            recommendations = gen_ai._generate_completion(
                                prompt,
                                "You are a clinical trial quality improvement consultant."
                            )
                            st.markdown(f"### Detailed Recommendations\n\n{recommendations}")
        
        with col2:
            st.metric("Total Subjects", len(subject_df))
            clean_rate = (subject_df["is_clean_patient"].sum() / len(subject_df) * 100) if "is_clean_patient" in subject_df.columns else 0
            st.metric("Clean Rate", f"{clean_rate:.1f}%")
            avg_dqi = subject_df["dqi_score"].mean() if "dqi_score" in subject_df.columns else 0
            st.metric("Avg DQI", f"{avg_dqi:.1f}")
    else:
        st.info("No subject data available for analysis")


def render_uploaded_deep_dive(study_name, all_metrics):
    """Render deep dive analysis for uploaded data"""
    st.subheader("🔍 Deep Dive Analysis")
    st.markdown("*Advanced AI-powered analysis of specific issues*")
    
    gen_ai = GenerativeAI()
    study_metrics = all_metrics.get(study_name, {})
    subject_df = study_metrics.get("subject_metrics", pd.DataFrame())
    
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["Query Hotspot Analysis", "Site Performance Patterns", "Data Completeness Trends", "Risk Factor Correlation"]
    )
    
    if st.button("Run Deep Dive Analysis", key="upload_deep_dive"):
        with st.spinner(f"Running {analysis_type} with Gemini AI..."):
            if not subject_df.empty:
                if analysis_type == "Query Hotspot Analysis":
                    total_queries = subject_df["open_queries"].sum() if "open_queries" in subject_df.columns else 0
                    context = f"Total open queries in {study_name}: {total_queries}\n"
                    
                    prompt = f"""{context}\nAnalyze query patterns and identify:
1. Root causes of high query volumes
2. Patterns in query distribution across sites
3. Specific actions to reduce queries
4. Expected timeline for improvements"""
                
                elif analysis_type == "Site Performance Patterns":
                    sites = subject_df["site_id"].nunique() if "site_id" in subject_df.columns else 0
                    context = f"Study {study_name} has {sites} sites\n"
                    
                    prompt = f"""{context}\nAnalyze site performance patterns:
1. Identify top and bottom performing sites
2. Common characteristics of high-performing sites
3. Interventions for underperforming sites
4. Best practices to replicate across sites"""
                
                elif analysis_type == "Data Completeness Trends":
                    missing_v = subject_df["missing_visits"].sum() if "missing_visits" in subject_df.columns else 0
                    missing_p = subject_df["missing_pages"].sum() if "missing_pages" in subject_df.columns else 0
                    context = f"Missing visits: {missing_v}, Missing pages: {missing_p}\n"
                    
                    prompt = f"""{context}\nAnalyze data completeness:
1. Primary drivers of missing data
2. Impact on study timeline and quality
3. Targeted interventions to improve completeness
4. Monitoring strategy going forward"""
                
                else:  # Risk Factor Correlation
                    high_risk = (subject_df["risk_level"] == "High").sum() if "risk_level" in subject_df.columns else 0
                    context = f"High risk subjects: {high_risk}\n"
                    
                    prompt = f"""{context}\nAnalyze risk factors:
1. What factors correlate with high risk?
2. Are there patterns across sites or subjects?
3. Predictive indicators for future risk
4. Preventive measures to implement"""
                
                analysis = gen_ai._generate_completion(
                    prompt,
                    "You are a clinical trial data analytics expert."
                )
                st.markdown(f"### {analysis_type}\n\n{analysis}")
            else:
                st.warning("Insufficient data for deep dive analysis")


def render_uploaded_ask_ai(study_name, study_metrics, study_df):
    """Render Ask AI chatbot for uploaded data"""
    st.subheader("💬 Ask AI About Your Study")
    st.markdown("*Ask any question about your uploaded data*")
    
    gen_ai = GenerativeAI()
    subject_df = study_metrics.get("subject_metrics", pd.DataFrame())
    
    # Provide some context about available data
    with st.expander("ℹ️ What can I ask?"):
        st.markdown("""
        **Example questions:**
        - What are the main quality issues in my study?
        - How can I improve the clean data rate?
        - Which sites need the most attention?
        - What's causing the high query volume?
        - How does my DQI score compare to industry standards?
        - What should I prioritize this week?
        - Are there any concerning trends in the data?
        """)
    
    # Chat interface
    user_question = st.text_area(
        "Your Question:",
        placeholder="e.g., What are the top 3 actions I should take to improve data quality?",
        height=100
    )
    
    if st.button("Ask AI", key="upload_ask_ai", type="primary"):
        if user_question:
            with st.spinner("Thinking..."):
                # Build context about the study
                context = {
                    "study_name": study_name,
                    "total_subjects": len(subject_df)
                }
                
                if not subject_df.empty:
                    if "dqi_score" in subject_df.columns:
                        context["average_dqi"] = round(subject_df['dqi_score'].mean(), 1)
                    if "is_clean_patient" in subject_df.columns:
                        clean_pct = (subject_df["is_clean_patient"].sum() / len(subject_df) * 100)
                        context["clean_data_rate_pct"] = round(clean_pct, 1)
                    if "open_queries" in subject_df.columns:
                        context["total_open_queries"] = int(subject_df['open_queries'].sum())
                    if "risk_level" in subject_df.columns:
                        high_risk = (subject_df["risk_level"] == "High").sum()
                        context["high_risk_subjects"] = int(high_risk)
                
                answer = gen_ai.answer_natural_language_query(user_question, context)
                st.success("✅ Answer:")
                st.markdown(answer)
        else:
            st.warning("Please enter a question")


def render_sidebar():
    """Render sidebar navigation"""
    st.sidebar.title("Navigation")
    
    page = st.sidebar.radio("Select View", [
        "📤 Upload & Analyze",
        "📊 Executive Dashboard",
        "🔍 Study Analysis",
        "📈 CRA Dashboard",
        "🤖 AI Insights",
        "⚙️ Settings"
    ])
    
    # Sub-navigation for Upload & Analyze
    uploaded_tab = None
    if page == "📤 Upload & Analyze":
        if 'uploaded_study_name' in st.session_state and st.session_state.uploaded_study_name:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Analysis Tabs")
            uploaded_tab = st.sidebar.radio(
                "Choose Analysis:",
                [
                    "📊 Overview",
                    "🏥 Site Performance",
                    "📝 Query Management",
                    "⚠️ Action Items",
                    "📋 Executive Summary",
                    "⚠️ Critical Actions",
                    "📊 Study-Level Insights",
                    "🔍 Deep Dive Analysis",
                    "💬 Ask AI"
                ],
                key="uploaded_analysis_tab"
            )
    
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **About**
    
    Clinical Trial Intelligence Platform
    
    Integrated insight-driven dataflow for clinical trials using Generative and Agentic AI.
    
    **Features:**
    - Real-time metrics
    - Data Quality Index
    - Risk detection
    - AI insights
    - Upload your own data
    """)
    
    return page, uploaded_tab


def main():
    """Main application entry point"""
    render_header()
    
    # Load data
    all_data, all_metrics, canonical_entities, risk_engine = load_and_process_data()
    
    # Merge uploaded data if available
    if all_data is None:
        all_data = {}
    if all_metrics is None:
        all_metrics = {}
    
    if 'uploaded_study_name' in st.session_state and st.session_state.uploaded_study_name:
        all_data[st.session_state.uploaded_study_name] = st.session_state.uploaded_study_df
        all_metrics[st.session_state.uploaded_study_name] = st.session_state.uploaded_study_metrics
        
        # Rebuild risk engine with uploaded data
        if all_metrics:
            risk_engine = RiskIntelligence(all_metrics)
    
    # Sidebar navigation
    page, uploaded_tab = render_sidebar()
    
    # Render selected page
    if page == "📊 Executive Dashboard":
        render_executive_dashboard(all_metrics, risk_engine)
    elif page == "🔍 Study Analysis":
        render_study_view(all_metrics, risk_engine)
    elif page == "📈 CRA Dashboard":
        render_cra_dashboard(all_data, all_metrics, canonical_entities, risk_engine)
    elif page == "🤖 AI Insights":
        render_ai_insights_page(all_data, all_metrics, risk_engine)
    elif page == "📤 Upload & Analyze":
        render_upload_analyze(uploaded_tab)
    elif page == "⚙️ Settings":
        st.header("⚙️ Settings")
        st.write("Configuration options:")
        st.text_input("Data Directory", str(DATA_PATH), disabled=True)
        st.info("API keys and other settings are configured in the .env file.")


if __name__ == "__main__":
    main()


