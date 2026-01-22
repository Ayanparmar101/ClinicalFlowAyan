import pandas as pd
from pathlib import Path

study_path = Path("data/raw/study_01")

# Find CPID file
cpid_file = None
for file in study_path.iterdir():
    if "cpid" in file.name.lower() and "metrics" in file.name.lower():
        cpid_file = file
        break

if cpid_file is None:
    raise Exception("CPID file not found")

print("Found file:", cpid_file.name)

# 1️⃣ Read WITHOUT header first to handle multi-row messy headers
df_raw = pd.read_excel(cpid_file, header=None)

# 2️⃣ Find the data start row (after 'Responsible LF for action')
# And find column indices for our targets
targets = {
    "Project Name": "project_name",
    "Region": "region",
    "Country": "country",
    "Site ID": "site_id",
    "Subject ID": "subject_id",
    "Missing Visits": "missing_visits",
    "Missing Page": "missing_pages",
    "#Total Queries": "total_queries"
}

col_map = {}
data_start_row = 0

for idx, row in df_raw.iloc[:10].iterrows():
    # Check for targets in this row
    for col_idx, cell_val in enumerate(row):
        cell_str = str(cell_val)
        for target_name, clean_name in targets.items():
            if clean_name not in col_map.values() and target_name in cell_str:
                col_map[col_idx] = clean_name
    
    # Check if this is the start of data (search in the whole row if needed)
    if any("Responsible LF for action" in str(val) for val in row):
        data_start_row = idx + 1

# 3️⃣ Extract and clean
df = df_raw.iloc[data_start_row:].copy()
df = df[list(col_map.keys())].rename(columns=col_map)
df = df.dropna(subset=["project_name"])
df = df.reset_index(drop=True)

print("\nCleaned Columns:")
print(df.columns.tolist())

print("\nFirst 5 clean rows:")
print(df.head())

# 6️⃣ Save for next steps
Path("data/processed").mkdir(parents=True, exist_ok=True)
df.to_parquet("data/processed/cpid_clean.parquet", index=False)
print("\n✅ Saved to data/processed/cpid_clean.parquet")
