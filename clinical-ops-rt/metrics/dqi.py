def calculate_dqi(state):
    """
    Risk-weighted Data Quality Index
    """
    dqi = 100

    dqi -= state.missing_visits * 5
    dqi -= state.missing_pages * 3
    dqi -= state.total_queries * 4

    if state.pending_sae:
        dqi -= 8

    dqi -= state.uncoded_terms * 2
    dqi -= state.overdue_signatures * 10

    state.dqi = max(dqi, 0)
    state.clean = state.dqi == 100
