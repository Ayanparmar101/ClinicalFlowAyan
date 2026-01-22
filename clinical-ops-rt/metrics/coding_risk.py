from metrics.dqi import calculate_dqi


def apply_coding_risk(states, coding_df):
    """
    Updates SubjectState based on uncoded terms.
    Emits events when subject enters coding backlog state.
    """
    events = {}

    # Count uncoded terms per subject
    for _, row in coding_df.iterrows():
        subject_id = row["subject_id"]
        require = str(row["require_coding"]).lower()
        status = str(row["coding_status"]).lower()

        if require == "yes" and status != "coded":
            events.setdefault(subject_id, 0)
            events[subject_id] += 1

    output_events = []

    for subject_id, count in events.items():
        if subject_id not in states:
            continue

        state = states[subject_id]

        if state.uncoded_terms == 0 and count > 0:
            state.uncoded_terms = count
            calculate_dqi(state)

            output_events.append({
                "type": "CODING_BACKLOG",
                "subject_id": subject_id,
                "site_id": state.site_id,
                "uncoded_terms": count,
                "new_dqi": state.dqi
            })

    return output_events
