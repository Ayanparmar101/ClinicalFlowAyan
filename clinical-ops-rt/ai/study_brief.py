def generate_study_brief(study_summary):
    ready = study_summary["ready_sites"]
    near = study_summary["near_ready_sites"]
    risk = study_summary["at_risk_sites"]
    not_ready = study_summary["not_ready_sites"]
    total = study_summary["total_sites"]

    if ready == total:
        return (
            f"All {total} sites are READY for database lock. "
            f"No blocking operational risks detected."
        )

    brief = []
    brief.append(
        f"The study currently has {ready} out of {total} sites READY for DB lock."
    )

    if near > 0:
        brief.append(
            f"{near} sites are NEAR READY and may reach DB lock with minimal remediation."
        )

    if risk > 0:
        brief.append(
            f"{risk} sites are AT RISK due to unresolved operational issues."
        )

    if not_ready > 0:
        brief.append(
            f"{not_ready} sites are NOT READY and require immediate intervention."
        )

    brief.append(
        "Primary risks include missing CRF pages, inactivated forms with data, "
        "pending SAEs, and coding backlogs."
    )

    return " ".join(brief)
