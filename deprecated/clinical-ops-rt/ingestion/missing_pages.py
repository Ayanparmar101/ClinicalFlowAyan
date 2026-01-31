import pandas as pd

def load_missing_pages(file_path):
    df = pd.read_excel(file_path)
    mapping = {
        'Subject Name': 'subject_id',
        '# of Days Missing': 'days_missing'
    }
    present_cols = [c for c in mapping.keys() if c in df.columns]
    return df[present_cols].rename(columns=mapping)
