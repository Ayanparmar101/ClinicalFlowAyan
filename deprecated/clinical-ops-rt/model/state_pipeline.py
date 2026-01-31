from pathlib import Path

from model.subject_factory import build_subject_states
from model.site_factory import build_site_states
from events.bus import EventBus

from ingestion.visit_projection import load_visit_projection
from ingestion.sae_dashboard import load_sae_dashboard
from ingestion.coding_reports import load_coding_report
from ingestion.missing_pages import load_missing_pages
from ingestion.inactivated_forms import load_inactivated_forms

from metrics.visit_risk import apply_visit_projection
from metrics.sae_risk import apply_sae_risk
from metrics.coding_risk import apply_coding_risk
from metrics.page_risk import apply_missing_pages
from metrics.inactivation_risk import apply_inactivation_risk


def build_full_state(df, study_id, study_path: Path):
    """
    Builds full subject + site state by applying ALL risk domains
    and collecting emitted events.
    """

    # 0️⃣ Event bus (single source of truth)
    event_bus = EventBus()

    # 1️⃣ Base subject state
    subject_states = build_subject_states(df, study_id)

    # 2️⃣ Visit Projection
    visit_file = next(
        f for f in study_path.iterdir()
        if "visit" in f.name.lower() and "projection" in f.name.lower()
    )
    visit_df = load_visit_projection(visit_file)
    visit_events = apply_visit_projection(subject_states, visit_df)
    event_bus.extend(visit_events)

    # 3️⃣ SAE Dashboard
    sae_file = next(
        f for f in study_path.iterdir()
        if "sae" in f.name.lower()
    )
    sae_df = load_sae_dashboard(sae_file)
    sae_events = apply_sae_risk(subject_states, sae_df)
    event_bus.extend(sae_events)

    # 4️⃣ Coding Reports (MedDRA + WHODD)
    for f in study_path.iterdir():
        name = f.name.lower()
        if "meddra" in name or "whod" in name:
            coding_df = load_coding_report(f)
            coding_events = apply_coding_risk(subject_states, coding_df)
            event_bus.extend(coding_events)

    # 5️⃣ Missing Pages
    pages_file = next(
        f for f in study_path.iterdir()
        if "missing" in f.name.lower() and "pages" in f.name.lower()
    )
    pages_df = load_missing_pages(pages_file)
    page_events = apply_missing_pages(subject_states, pages_df)
    event_bus.extend(page_events)

    # 6️⃣ Inactivated Forms
    inact_file = next(
        f for f in study_path.iterdir()
        if "inactivated" in f.name.lower()
    )
    inact_df = load_inactivated_forms(inact_file)
    inact_events = apply_inactivation_risk(subject_states, inact_df)
    event_bus.extend(inact_events)

    # 7️⃣ Aggregate to sites AFTER all mutations
    site_states = build_site_states(subject_states)

    return subject_states, site_states, event_bus
