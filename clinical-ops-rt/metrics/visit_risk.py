from metrics.dqi import calculate_dqi


def apply_visit_projection(states, visit_df):
    """
    Updates SubjectState objects based on overdue visits.
    Emits events on state change.
    """
    events = []

    for _, row in visit_df.iterrows():
        subject_id = row["subject"]
        days = row["days_outstanding"]

        if subject_id not in states:
            continue

        state = states[subject_id]

        if days > 0:
            if state.missing_visits == 0:
                state.missing_visits = 1
                calculate_dqi(state)

                events.append({
                    "type": "VISIT_OVERDUE",
                    "subject_id": subject_id,
                    "site_id": state.site_id,
                    "days_outstanding": int(days),
                    "new_dqi": state.dqi
                })

    return events
