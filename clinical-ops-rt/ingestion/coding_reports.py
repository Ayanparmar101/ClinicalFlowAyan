import pandas as pd


def load_coding_report(file_path):
    df = pd.read_excel(file_path)

    df.columns = (
        df.columns
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
    )

    # Normalize subject column
    if "subject" in df.columns:
        df["subject_id"] = df["subject"]
    elif "subject_id" not in df.columns:
        raise ValueError("No subject column found in coding report")

    required = ["subject_id", "coding_status", "require_coding"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"Missing columns in coding report: {missing}")

    return df[required]
