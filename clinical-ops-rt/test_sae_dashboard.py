from pathlib import Path
import pandas as pd
from model.subject_factory import build_subject_states
from ingestion.sae_dashboard import load_sae_dashboard
from metrics.sae_risk import apply_sae_risk

# Load subject states
df = pd.read_parquet("data/processed/cpid_clean.parquet")
states = build_subject_states(df, study_id="study_01")

# Locate SAE file
study_path = Path("data/raw/study_01")

sae_file = None
for f in study_path.iterdir():
    if "sae" in f.name.lower():
        sae_file = f
        break

if sae_file is None:
    raise Exception("SAE dashboard file not found")

print("Using SAE file:", sae_file.name)

sae_df = load_sae_dashboard(sae_file)

events = apply_sae_risk(states, sae_df)

print("\nSAE EVENTS:")
for e in events[:5]:
    print(e)

print("\nUPDATED SUBJECT STATES:")
for i, s in enumerate(states.values()):
    print(s)
    if i == 4:
        break
