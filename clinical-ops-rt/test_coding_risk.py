from pathlib import Path
import pandas as pd
from model.subject_factory import build_subject_states
from ingestion.coding_reports import load_coding_report
from metrics.coding_risk import apply_coding_risk

# Load base subject states
df = pd.read_parquet("data/processed/cpid_clean.parquet")
states = build_subject_states(df, study_id="study_01")

study_path = Path("data/raw/study_01")

coding_files = []
for f in study_path.iterdir():
    name = f.name.lower()
    if "meddra" in name or "whod" in name:
        coding_files.append(f)

if not coding_files:
    raise Exception("No coding reports found")

all_events = []

for f in coding_files:
    print("Processing:", f.name)
    coding_df = load_coding_report(f)
    events = apply_coding_risk(states, coding_df)
    all_events.extend(events)

print("\nCODING EVENTS:")
for e in all_events[:5]:
    print(e)

print("\nUPDATED SUBJECT STATES:")
for i, s in enumerate(states.values()):
    print(s)
    if i == 4:
        break
