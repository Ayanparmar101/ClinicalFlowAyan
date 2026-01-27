from pathlib import Path
import re

RAW_PATH = Path("data/raw")

for folder in RAW_PATH.iterdir():
    if not folder.is_dir():
        continue

    # Extract study number using regex
    match = re.search(r"study[_\s]*(\d+)", folder.name.lower())
    if not match:
        print(f"Skipping: {folder.name}")
        continue

    study_num = int(match.group(1))
    new_name = f"study_{study_num:02d}"
    new_path = RAW_PATH / new_name

    if new_path.exists():
        print(f"Already exists: {new_name}")
        continue

    print(f"Renaming: {folder.name} → {new_name}")
    folder.rename(new_path)
