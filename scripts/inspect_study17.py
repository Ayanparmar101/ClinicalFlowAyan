"""Check actual columns from Study 17"""
import pandas as pd

file = r"C:\Users\Ayan Parmar\Desktop\NestTry\data\Study 17_CPID_Input Files - Anonymization\CPID_EDC Metrics_updated.xlsx"
df = pd.read_excel(file)

print("="*70)
print(f"Study 17 EDC Metrics - Shape: {df.shape}")
print("="*70)
print("\nColumns:")
for i, col in enumerate(df.columns, 1):
    print(f"{i:2}. {col}")

print("\n" + "="*70)
print("Sample data (first 3 rows, key columns):")
print("="*70)
# Show first few columns
print(df.iloc[:3, :10])

print("\n" + "="*70)
print("Column Data Types:")
print("="*70)
print(df.dtypes)

print("\n" + "="*70)
print("Summary Statistics:")
print("="*70)
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
print(df[numeric_cols].describe())
