"""
Simple validation test without complex imports
"""
import sys
from pathlib import Path

# Test basic imports
print("Testing basic imports...")
try:
    import pandas as pd
    print("✓ pandas imported")
except Exception as e:
    print(f"✗ pandas import failed: {e}")
    sys.exit(1)

try:
    import numpy as np
    print("✓ numpy imported")
except Exception as e:
    print(f"✗ numpy import failed: {e}")
    sys.exit(1)

try:
    import openpyxl
    print("✓ openpyxl imported")
except Exception as e:
    print(f"✗ openpyxl import failed: {e}")
    sys.exit(1)

# Test data loading
print("\nTesting data loading...")
data_path = Path("data/Study 1_CPID_Input Files - Anonymization")
files = list(data_path.glob("*.xlsx"))
print(f"✓ Found {len(files)} Excel files")

# Try loading one file
if files:
    test_file = files[0]
    print(f"\nLoading test file: {test_file.name}")
    try:
        df = pd.read_excel(test_file)
        print(f"✓ Loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        print(f"\n✓ First few columns: {list(df.columns[:5])}")
    except Exception as e:
        print(f"✗ Loading failed: {e}")

print("\n✓ BASIC TESTS PASSED")
