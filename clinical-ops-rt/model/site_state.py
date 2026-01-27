class SiteState:
    def __init__(self, site_id, region=None):
        self.site_id = site_id
        self.region = region
        self.subjects = []

        self.total_subjects = 0
        self.clean_subjects = 0
        self.blocking_subjects = 0

        self.avg_dqi = 100
        self.min_dqi = 100

        self.ready_for_db_lock = True
        self.readiness_tier = None  # ✅ NEW

    def compute(self):
        self.total_subjects = len(self.subjects)
        if self.total_subjects == 0:
            return

        dqis = [s.dqi for s in self.subjects]

        self.avg_dqi = round(sum(dqis) / len(dqis), 1)
        self.min_dqi = min(dqis)

        self.clean_subjects = sum(1 for s in self.subjects if s.clean)
        self.blocking_subjects = self.total_subjects - self.clean_subjects

        # Binary DB lock readiness (strict, regulatory)
        self.ready_for_db_lock = self.blocking_subjects == 0

        # ✅ NEW: Readiness tiers (operational, human-friendly)
        if self.blocking_subjects == 0:
            self.readiness_tier = "READY"
        elif self.blocking_subjects <= 1:
            self.readiness_tier = "NEAR_READY"
        elif self.blocking_subjects <= 3:
            self.readiness_tier = "AT_RISK"
        else:
            self.readiness_tier = "NOT_READY"

    def __repr__(self):
        return (
            f"<SiteState {self.site_id} | "
            f"Region={self.region} | "
            f"Subjects={self.total_subjects} | "
            f"Blocking={self.blocking_subjects} | "
            f"AvgDQI={self.avg_dqi} | "
            f"Tier={self.readiness_tier} | "
            f"Ready={self.ready_for_db_lock}>"
        )
