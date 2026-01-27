def generate_site_narrative(site_state, explanation, priorities):
    """
    Generate a human-readable operational narrative
    """

    if site_state.ready_for_db_lock:
        return (
            f"Site {site_state.site_id} is READY for DB lock. "
            f"All subjects are clean with an average DQI of {site_state.avg_dqi}."
        )

    narrative = []
    narrative.append(
        f"Site {site_state.site_id} is currently {site_state.readiness_tier.replace('_', ' ')} "
        f"with an average DQI of {site_state.avg_dqi}."
    )

    narrative.append(
        f"There are {site_state.blocking_subjects} blocking subjects preventing DB lock."
    )

    if explanation.get("reasons"):
        narrative.append("Primary operational issues identified:")
        for r in explanation["reasons"]:
            narrative.append(f"- {r}")

    if priorities:
        top = priorities[0]
        narrative.append(
            f"Highest priority action is for {top['subject_id']} "
            f"(current DQI {top['current_dqi']})."
        )
        for action in top["recommended_actions"]:
            narrative.append(f"- {action}")

    return " ".join(narrative)
