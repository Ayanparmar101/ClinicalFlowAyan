import pandas as pd


def load_sae_dashboard(file_path):
    df = pd.read_excel(file_path)

    # Robust column mapping
    mapping = {}
    for col in df.columns:
        c = col.lower()
        if 'patient' in c or 'subject' in c:
            mapping[col] = 'subject_id'
        elif 'review' in c and 'status' in c:
            mapping[col] = 'review_status'
        elif 'action' in c and 'status' in c:
            mapping[col] = 'action_status'

    df = df.rename(columns=mapping)
    required = ["subject_id", "review_status"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns in SAE dashboard: {missing}. Found: {df.columns.tolist()}")

    return df[required]
