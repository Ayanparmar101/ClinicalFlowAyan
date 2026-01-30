import pandas as pd
from pathlib import Path
from model.state_pipeline import build_full_state

df = pd.read_parquet("data/processed/cpid_clean.parquet")
study_path = Path("data/raw/study_01")

subject_states, site_states, event_bus = build_full_state(
    df=df,
    study_id="study_01",
    study_path=study_path
)

print(f"Total Subjects: {len(subject_states)}")
print(f"Total Sites: {len(site_states)}")
print(f"Total Events: {len(event_bus.get_events())}")

print("\nSAMPLE SITE STATES:")
for s in list(site_states.values())[:5]:
    print(s)
