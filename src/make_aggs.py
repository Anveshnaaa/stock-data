from pathlib import Path
import pandas as pd

# Paths
CLEANED_PARQUET_PATH = Path("data/processed/cleaned.parquet")
AGG1_PATH = Path("data/processed/agg1.parquet")
AGG2_PATH = Path("data/processed/agg2.parquet")


def main():
    print(f"Loading cleaned parquet from {CLEANED_PARQUET_PATH}...")
    df = pd.read_parquet(CLEANED_PARQUET_PATH)
    print("Cleaned shape:", df.shape)
    print("Columns:", list(df.columns))

    # We know from data_clean:
    # trade_date: datetime
    # ticker: string
    # close_price: numeric
    # volume: numeric

    # 1. Ensure trade_date is datetime
    df["trade_date"] = pd.to_datetime(df["trade_date"], errors="coerce")

    # 2. Make sure close_price and volume are numeric
    df["close_price"] = pd.to_numeric(df["close_price"], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    # Drop rows with missing values in these important columns
    df = df.dropna(subset=["trade_date", "ticker", "close_price", "volume"])

    # --- Aggregation 1: daily avg close price by ticker ---
    agg1 = (
        df.groupby(["trade_date", "ticker"], as_index=False)["close_price"]
        .mean()
        .rename(columns={"close_price": "avg_close"})
    )

    # --- Aggregation 2: average volume by ticker across all dates ---
    agg2 = (
        df.groupby("ticker", as_index=False)["volume"]
        .mean()
        .rename(columns={"volume": "avg_volume"})
    )

    print("\nAGG1 (daily avg close) preview:")
    print(agg1.head())

    print("\nAGG2 (avg volume by ticker) preview:")
    print(agg2.head())

    # Save both as parquet
    AGG1_PATH.parent.mkdir(parents=True, exist_ok=True)
    agg1.to_parquet(AGG1_PATH, index=False)
    agg2.to_parquet(AGG2_PATH, index=False)

    print(f"\nSaved agg1 to {AGG1_PATH}")
    print(f"Saved agg2 to {AGG2_PATH}")


if __name__ == "__main__":
    main()

