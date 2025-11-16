from pathlib import Path
import pandas as pd

# Path to your the CSV pulled from github
csv_path = Path("data/raw/stock_market.csv")

print("Loading:", csv_path)
df = pd.read_csv(csv_path)

print("\n=== SHAPE ===")
print(df.shape)

print("\n=== COLUMNS ===")
print(df.columns)

print("\n=== HEAD ===")
print(df.head())

print("\n=== INFO ===")
print(df.info())
