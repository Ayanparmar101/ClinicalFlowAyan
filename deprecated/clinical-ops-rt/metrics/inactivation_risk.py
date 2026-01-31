from metrics.dqi import calculate_dqi


def apply_inactivation_risk(states, inact_df):
    events = []

    for _, row in inact_df.iterrows():
        subject_id = str(row["subject_id"])
        data_present = str(row["data_present"]).lower()
        action = str(row["action"]).lower()

        if subject_id not in states:
            continue

        if data_present == "y" and "inactivated" in action:
            state = states[subject_id]

            if state.overdue_signatures == 0:
                state.overdue_signatures = 1
                calculate_dqi(state)

                events.append({
                    "type": "INACTIVATED_FORM",
                    "subject_id": subject_id,
                    "site_id": state.site_id,
                    "new_dqi": state.dqi
                })

    return events
