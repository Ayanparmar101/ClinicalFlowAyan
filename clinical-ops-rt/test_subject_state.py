import pandas as pd
from pathlib import Path
from model.subject_factory import build_subject_states

# Load your cleaned CPID dataframe
df = pd.read_parquet("data/processed/cpid_clean.parquet") if Path(
    "data/processed/cpid_clean.parquet"
).exists() else None

if df is None:
    print("⚠️  Using in-memory dataframe from last step")

    # TEMP: recreate df from CSV/Excel if needed
    raise Exception(
        "Save your cleaned dataframe to data/processed/cpid_clean.pkl first"
    )

states = build_subject_states(df, study_id="study_01")

# Print first 5 subject states
for i, s in enumerate(states.values()):
    print(s)
    if i == 4:
        break
