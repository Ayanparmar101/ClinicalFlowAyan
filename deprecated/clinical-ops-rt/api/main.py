# API entry point
from fastapi import FastAPI
from pathlib import Path
import pandas as pd
from ai.explainer import explain_site
from ai.prioritizer import prioritize_site_actions
from ai.narrative import generate_site_narrative
from ai.explainer import explain_site
from ai.prioritizer import prioritize_site_actions
from ai.study_brief import generate_study_brief




from model.state_pipeline import build_full_state

app = FastAPI(
    title="Clinical Ops Real-Time Intelligence",
    description="Real-time operational readiness for clinical trials"
)

# Load data once (hackathon mode)
DATA_PATH = Path("data/processed/cpid_clean.parquet")
STUDY_PATH = Path("data/raw/study_01")

@app.get("/")
def root():
    return {"status": "ok", "message": "Clinical Ops RT Engine running"}

@app.get("/study/summary")
def study_summary():
    df = pd.read_parquet(DATA_PATH)
    subject_states, site_states, event_bus = build_full_state(
        df=df,
        study_id="study_01",
        study_path=STUDY_PATH
    )

    return {
        "study_id": "study_01",
        "total_subjects": len(subject_states),
        "total_sites": len(site_states),
        "ready_sites": sum(1 for s in site_states.values() if s.ready_for_db_lock),
        "near_ready_sites": sum(1 for s in site_states.values() if s.readiness_tier == "NEAR_READY"),
        "at_risk_sites": sum(1 for s in site_states.values() if s.readiness_tier == "AT_RISK"),
        "not_ready_sites": sum(1 for s in site_states.values() if s.readiness_tier == "NOT_READY"),
        "events_generated": len(event_bus.get_events())
    }

@app.get("/sites")
def get_sites():
    df = pd.read_parquet(DATA_PATH)
    _, site_states, _ = build_full_state(
        df=df,
        study_id="study_01",
        study_path=STUDY_PATH
    )

    return [
        {
            "site_id": s.site_id,
            "region": s.region,
            "subjects": s.total_subjects,
            "blocking_subjects": s.blocking_subjects,
            "avg_dqi": s.avg_dqi,
            "readiness_tier": s.readiness_tier,
            "ready_for_db_lock": s.ready_for_db_lock
        }
        for s in site_states.values()
    ]

@app.get("/subjects")
def get_subjects():
    df = pd.read_parquet(DATA_PATH)
    subject_states, _, _ = build_full_state(
        df=df,
        study_id="study_01",
        study_path=STUDY_PATH
    )

    return [
        {
            "subject_id": s.subject_id,
            "site_id": s.site_id,
            "dqi": s.dqi,
            "clean": s.clean,
            "missing_visits": s.missing_visits,
            "missing_pages": s.missing_pages,
            "total_queries": s.total_queries,
            "pending_sae": s.pending_sae,
            "uncoded_terms": s.uncoded_terms,
            "overdue_signatures": s.overdue_signatures
        }
        for s in subject_states.values()
    ]

@app.get("/events")
def get_events():
    df = pd.read_parquet(DATA_PATH)
    _, _, event_bus = build_full_state(
        df=df,
        study_id="study_01",
        study_path=STUDY_PATH
    )

    return [e.to_dict() for e in event_bus.get_events()]

@app.get("/ai/explain/site/{site_id}")
def explain_site_endpoint(site_id: str):
    df = pd.read_parquet(DATA_PATH)

    subject_states, site_states, event_bus = build_full_state(
        df=df,
        study_id="study_01",
        study_path=STUDY_PATH
    )

    site = site_states.get(site_id)
    if not site:
        return {"error": f"Site {site_id} not found"}

    explanation = explain_site(
        site_state=site,
        events=event_bus.get_events()
    )

    return explanation

@app.get("/ai/prioritize/site/{site_id}")
def prioritize_site(site_id: str):
    df = pd.read_parquet(DATA_PATH)

    subject_states, site_states, event_bus = build_full_state(
        df=df,
        study_id="study_01",
        study_path=STUDY_PATH
    )

    site = site_states.get(site_id)
    if not site:
        return {"error": f"Site {site_id} not found"}

    priorities = prioritize_site_actions(
        site_state=site,
        subject_states=subject_states,
        events=event_bus.get_events()
    )

    return {
        "site_id": site_id,
        "readiness_tier": site.readiness_tier,
        "priorities": priorities
    }

@app.get("/ai/brief/site/{site_id}")
def site_operational_brief(site_id: str):
    df = pd.read_parquet(DATA_PATH)

    subject_states, site_states, event_bus = build_full_state(
        df=df,
        study_id="study_01",
        study_path=STUDY_PATH
    )

    site = site_states.get(site_id)
    if not site:
        return {"error": f"Site {site_id} not found"}

    explanation = explain_site(
        site_state=site,
        events=event_bus.get_events()
    )
    priorities = prioritize_site_actions(
        site_state=site,
        subject_states=subject_states,
        events=event_bus.get_events()
    )

    narrative = generate_site_narrative(site, explanation, priorities)

    return {
        "site_id": site_id,
        "narrative": narrative,
        "explanation": explanation,
        "priorities": priorities
    }

@app.get("/ai/brief/study")
def study_ai_brief():
    df = pd.read_parquet(DATA_PATH)

    subject_states, site_states, event_bus = build_full_state(
        df=df,
        study_id="study_01",
        study_path=STUDY_PATH
    )

    total_sites = len(site_states)

    ready = sum(1 for s in site_states.values() if s.ready_for_db_lock)
    near = sum(1 for s in site_states.values() if s.readiness_tier == "NEAR_READY")
    risk = sum(1 for s in site_states.values() if s.readiness_tier == "AT_RISK")
    not_ready = sum(1 for s in site_states.values() if s.readiness_tier == "NOT_READY")

    summary = {
        "study_id": "study_01",
        "total_sites": total_sites,
        "ready_sites": ready,
        "near_ready_sites": near,
        "at_risk_sites": risk,
        "not_ready_sites": not_ready,
    }

    brief = generate_study_brief(summary)

    return {
        "summary": summary,
        "ai_brief": brief
    }
