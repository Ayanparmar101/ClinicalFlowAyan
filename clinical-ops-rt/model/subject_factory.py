from model.state import SubjectState
from metrics.dqi import calculate_dqi


def build_subject_states(df, study_id):
    """
    Converts canonical CPID dataframe into live SubjectState objects
    """
    subject_states = {}

    for _, row in df.iterrows():
        state = SubjectState(
            study_id=study_id,
            project_name=row["project_name"],
            region=row["region"],
            country=row["country"],
            site_id=row["site_id"],
            subject_id=row["subject_id"],
            missing_visits=row["missing_visits"],
            missing_pages=row["missing_pages"],
            total_queries=row["total_queries"],
        )

        calculate_dqi(state)

        subject_states[state.subject_id] = state

    return subject_states
