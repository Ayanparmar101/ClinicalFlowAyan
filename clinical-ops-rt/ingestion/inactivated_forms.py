import pandas as pd


def load_inactivated_forms(file_path):
    df = pd.read_excel(file_path)

    # Robust column mapping
    mapping = {}
    for col in df.columns:
        c = col.lower()
        if 'subject' in c:
            mapping[col] = 'subject_id'
        elif 'audit' in c and 'action' in c:
            mapping[col] = 'action'
        elif 'data' in c and 'form' in c:
            mapping[col] = 'data_present'

    df = df.rename(columns=mapping)
    # Ensure critical columns are present
    required = ["subject_id", "action", "data_present"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns in Inactivated Forms: {missing}. Found: {df.columns.tolist()}")

    return df[required]
