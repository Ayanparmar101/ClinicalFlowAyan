class SubjectState:
    def __init__(
        self,
        study_id,
        project_name,
        region,
        country,
        site_id,
        subject_id,
        missing_visits,
        missing_pages,
        total_queries
    ):
        self.study_id = study_id
        self.project_name = project_name
        self.region = region
        self.country = country
        self.site_id = site_id
        self.subject_id = subject_id

        # Operational metrics (Safe for None and NaN)
        self.missing_visits = int(missing_visits) if missing_visits is not None and missing_visits == missing_visits else 0
        self.missing_pages = int(missing_pages) if missing_pages is not None and missing_pages == missing_pages else 0
        self.total_queries = int(total_queries) if total_queries is not None and total_queries == total_queries else 0

        # Future metrics (will be filled later)
        self.pending_sae = False
        self.uncoded_terms = 0
        self.overdue_signatures = 0

        # Computed fields
        self.dqi = None
        self.clean = None

    def __repr__(self):
        return (
            f"<SubjectState "
            f"{self.subject_id} | "
            f"Site={self.site_id} | "
            f"DQI={self.dqi}>"
        )
