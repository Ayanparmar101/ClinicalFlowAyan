import pandas as pd


def load_missing_pages(file_path):
    df = pd.read_excel(file_path)

    df.columns = (
        df.columns
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("#", "")
    )

    required = ["subjectname", "no._#days_page_missing"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns in Missing Pages report: {missing}")

    return df[required].rename(
        columns={
            "subjectname": "subject_id",
            "no._#days_page_missing": "days_missing"
        }
    )
