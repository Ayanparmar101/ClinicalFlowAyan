from collections import Counter


def explain_site(site_state, events):
    """
    Deterministic explanation for why a site is in its current readiness tier
    """

    site_id = site_state.site_id

    site_events = [
        e for e in events
        if (getattr(e, "site_id", None) == site_id) or (isinstance(e, dict) and e.get("site_id") == site_id)
    ]

    explanation = {
        "site_id": site_id,
        "region": site_state.region,
        "readiness_tier": site_state.readiness_tier,
        "avg_dqi": site_state.avg_dqi,
        "blocking_subjects": site_state.blocking_subjects,
        "reasons": [],
        "recommendations": []
    }

    # ---- Reasoning rules ----

    def get_event_type(e):
        if hasattr(e, "event_type"):
            return e.event_type
        if isinstance(e, dict):
            return e.get("event_type") or e.get("type")
        return "UNKNOWN"

    event_types = Counter(get_event_type(e) for e in site_events)

    if event_types.get("SAE_PENDING", 0) > 0:
        explanation["reasons"].append(
            f"{event_types['SAE_PENDING']} subjects have pending SAE reviews"
        )
        explanation["recommendations"].append(
            "Prioritize SAE review to reduce regulatory risk"
        )

    if event_types.get("VISIT_OVERDUE", 0) > 0:
        explanation["reasons"].append(
            f"{event_types['VISIT_OVERDUE']} overdue visits detected"
        )
        explanation["recommendations"].append(
            "Ensure overdue visits are completed or documented"
        )

    if event_types.get("CODING_BACKLOG", 0) > 0:
        explanation["reasons"].append(
            f"{event_types['CODING_BACKLOG']} uncoded medical terms pending"
        )
        explanation["recommendations"].append(
            "Clear MedDRA / WHODD coding backlog"
        )

    if event_types.get("MISSING_PAGES", 0) > 0:
        explanation["reasons"].append(
            f"{event_types['MISSING_PAGES']} missing CRF pages"
        )
        explanation["recommendations"].append(
            "Resolve missing pages before DB lock"
        )

    if event_types.get("INACTIVATED_FORM", 0) > 0:
        explanation["reasons"].append(
            f"{event_types['INACTIVATED_FORM']} inactivated CRFs with data"
        )
        explanation["recommendations"].append(
            "Reactivate or clean inactivated CRFs"
        )

    if not explanation["reasons"]:
        explanation["reasons"].append("No blocking operational risks detected")
        explanation["recommendations"].append(
            "Site is operationally clean"
        )

    return explanation
