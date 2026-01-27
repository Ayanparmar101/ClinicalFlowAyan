def prioritize_site_actions(site_state, subject_states, events):
    """
    Rank subjects at a site by operational impact
    """

    site_id = site_state.site_id

    # Subjects belonging to this site
    site_subjects = [
        s for s in subject_states.values()
        if s.site_id == site_id
    ]

    subject_events = {}
    for e in events:
        # Handle both Event objects and dictionaries safely
        sid = getattr(e, "subject_id", None) or (isinstance(e, dict) and e.get("subject_id"))
        if sid:
            subject_events.setdefault(sid, []).append(e)

    priorities = []

    for subject in site_subjects:
        if subject.clean:
            continue  # not blocking

        evs = subject_events.get(subject.subject_id, [])

        impact = 0
        reasons = []
        actions = []

        for e in evs:
            # Handle both Event objects and dictionaries safely
            etype = getattr(e, "event_type", None) or (isinstance(e, dict) and (e.get("event_type") or e.get("type")))
            if not etype:
                continue

            if etype == "SAE_PENDING":
                impact += 50
                reasons.append("Pending SAE review")
                actions.append("Complete SAE review")

            elif etype == "VISIT_OVERDUE":
                impact += 30
                reasons.append("Overdue visit")
                actions.append("Complete or document visit")

            elif etype == "CODING_BACKLOG":
                impact += 20
                reasons.append("Uncoded medical term")
                actions.append("Complete MedDRA/WHODD coding")

            elif etype == "MISSING_PAGES":
                impact += 25
                reasons.append("Missing CRF pages")
                actions.append("Resolve missing CRF pages")

            elif etype == "INACTIVATED_FORM":
                impact += 15
                reasons.append("Inactivated CRF with data")
                actions.append("Reactivate or clean CRF")

        priorities.append({
            "subject_id": subject.subject_id,
            "current_dqi": subject.dqi,
            "impact_score": impact,
            "reasons": list(set(reasons)),
            "recommended_actions": list(set(actions))
        })

    # Highest impact first
    priorities.sort(key=lambda x: x["impact_score"], reverse=True)

    return priorities
