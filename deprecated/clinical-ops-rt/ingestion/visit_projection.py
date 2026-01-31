import pandas as pd


def load_visit_projection(file_path):
    df = pd.read_excel(file_path)

    # Robust column mapping
    mapping = {}
    for col in df.columns:
        c = col.lower()
        if 'site' in c:
            mapping[col] = 'site'
        elif 'subject' in c:
            mapping[col] = 'subject'
        elif 'days' in c and 'outstanding' in c:
            mapping[col] = 'days_outstanding'

    df = df.rename(columns=mapping)
    required = ["site", "subject", "days_outstanding"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns in Visit Projection: {missing}. Found: {df.columns.tolist()}")

    return df[required]
