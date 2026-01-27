from pathlib import Path
from ingestion.visit_projection import load_visit_projection
from model.subject_factory import build_subject_states
import pandas as pd
from metrics.visit_risk import apply_visit_projection

# Load subject states
df = pd.read_parquet("data/processed/cpid_clean.parquet")
states = build_subject_states(df, study_id="study_01")

# Locate Visit Projection file
study_path = Path("data/raw/study_01")

visit_file = None
for f in study_path.iterdir():
    if "visit" in f.name.lower() and "projection" in f.name.lower():
        visit_file = f
        break

if visit_file is None:
    raise Exception("Visit Projection file not found")

print("Using file:", visit_file.name)

visit_df = load_visit_projection(visit_file)

events = apply_visit_projection(states, visit_df)

print("\nEVENTS:")
for e in events[:5]:
    print(e)

print("\nUPDATED SUBJECT STATES:")
for i, s in enumerate(states.values()):
    print(s)
    if i == 4:
        break
