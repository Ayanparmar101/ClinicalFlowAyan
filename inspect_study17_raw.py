"""Check actual structure of Study 17 file"""
import pandas as pd

file = r"C:\Users\Ayan Parmar\Desktop\NestTry\data\Study 17_CPID_Input Files - Anonymization\CPID_EDC Metrics_updated.xlsx"
df = pd.read_excel(file, header=None)  # Read without header

print("="*70)
print(f"Study 17 EDC Metrics - Raw Data")
print("="*70)
print("\nFirst 10 rows to understand structure:")
print(df.head(10))

print("\n\n" + "="*70)
print("Now let's try skipping rows and reading properly:")
print("="*70)
# Try reading with proper header rows
df2 = pd.read_excel(file, header=[0, 1])
print(f"Shape: {df2.shape}")
print("\nColumns (multi-index):")
for i, col in enumerate(df2.columns[:15], 1):
    print(f"{i:2}. {col}")

print("\n\nFirst 5 data rows:")
print(df2.head(5))
