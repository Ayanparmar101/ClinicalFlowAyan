import pandas as pd
from model.subject_factory import build_subject_states
from model.site_factory import build_site_states

df = pd.read_parquet("data/processed/cpid_clean.parquet")
subject_states = build_subject_states(df, study_id="study_01")

# ⚠️ IMPORTANT
# Re-apply all risks here if needed (visit, sae, coding, pages, inactivation)
# For now, assume you already applied them before aggregation

site_states = build_site_states(subject_states)

print("SITE STATES:")
for i, site in enumerate(site_states.values()):
    print(site)
    if i == 4:
        break
