from metrics.dqi import calculate_dqi


def apply_missing_pages(states, pages_df):
    events = []

    for _, row in pages_df.iterrows():
        subject_id = row["subject_id"]
        days = row["days_missing"]

        if subject_id not in states:
            continue

        if days > 0:
            state = states[subject_id]

            if state.missing_pages == 0:
                state.missing_pages = 1
                calculate_dqi(state)

                events.append({
                    "type": "MISSING_PAGES",
                    "subject_id": subject_id,
                    "site_id": state.site_id,
                    "new_dqi": state.dqi
                })

    return events
