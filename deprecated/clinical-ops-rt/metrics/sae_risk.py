from metrics.dqi import calculate_dqi


def apply_sae_risk(states, sae_df):
    """
    Updates SubjectState based on SAE review status.
    Emits events on transition to pending SAE.
    """
    events = []

    for _, row in sae_df.iterrows():
        subject_id = row["subject_id"]
        review_status = str(row["review_status"]).lower()

        if subject_id not in states:
            continue

        state = states[subject_id]

        if review_status != "review completed":
            if not state.pending_sae:
                state.pending_sae = True
                calculate_dqi(state)

                events.append({
                    "type": "SAE_PENDING",
                    "subject_id": subject_id,
                    "site_id": state.site_id,
                    "new_dqi": state.dqi
                })

    return events
