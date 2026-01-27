from pathlib import Path
import pandas as pd
from model.subject_factory import build_subject_states
from ingestion.missing_pages import load_missing_pages
from ingestion.inactivated_forms import load_inactivated_forms
from metrics.page_risk import apply_missing_pages
from metrics.inactivation_risk import apply_inactivation_risk

df = pd.read_parquet("data/processed/cpid_clean.parquet")
states = build_subject_states(df, study_id="study_01")

study_path = Path("data/raw/study_01")

# Missing pages
pages_file = next(f for f in study_path.iterdir() if "missing" in f.name.lower() and "pages" in f.name.lower())
pages_df = load_missing_pages(pages_file)
page_events = apply_missing_pages(states, pages_df)

# Inactivated forms
inact_file = next(f for f in study_path.iterdir() if "inactivated" in f.name.lower())
inact_df = load_inactivated_forms(inact_file)
inact_events = apply_inactivation_risk(states, inact_df)

print("\nPAGE EVENTS:", len(page_events))
print(page_events[:3])

print("\nINACTIVATION EVENTS:", len(inact_events))
print(inact_events[:3])

print("\nUPDATED SUBJECT STATES:")
for i, s in enumerate(states.values()):
    print(s)
    if i == 4:
        break
