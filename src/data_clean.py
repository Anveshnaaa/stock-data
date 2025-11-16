from pathlib import Path

import numpy as np
import pandas as pd

# Paths
RAW_CSV_PATH = Path("data/raw/stock_market.csv")
CLEANED_PARQUET_PATH = Path("data/processed/cleaned.parquet")

# Tokens that should be treated as missing
NA_TOKENS = {"", "na", "n/a", "null", "-"}


def main():
    print(f"Loading raw CSV from {RAW_CSV_PATH}...")
    df = pd.read_csv(RAW_CSV_PATH)
    print("Initial shape:", df.shape)

    # 1. Rename columns to snake_case (we know these from inspect_data.py)
    df = df.rename(
        columns={
            "Trade Date": "trade_date",
            "Ticker": "ticker",
            "Open Price": "open_price",
            "Close Price": "close_price",
            "Volume": "volume",
            "Sector": "sector",
            "Validated": "validated",
            "Currency": "currency",
            "Exchange": "exchange",
            "Notes": "notes",
        }
    )

    # 2. Strip whitespace and normalize NA tokens in ALL columns
    for col in df.columns:
        # convert to string then strip spaces
        df[col] = df[col].astype("string").str.strip()
        # replace things like "na", "N/A", "-", "" with NaN
        df[col] = df[col].replace(
            {val: np.nan for val in NA_TOKENS},
            regex=False,
        )

    # 3. Standardize text columns to lowercase (except date)
    text_cols = [
        "ticker",
        "sector",
        "validated",
        "currency",
        "exchange",
        "notes",
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].str.lower()

    # 4. Parse trade_date into datetime
    df["trade_date"] = pd.to_datetime(df["trade_date"], errors="coerce")
    # Drop any rows where date couldn't be parsed
    df = df.dropna(subset=["trade_date"])

    # 5. Create formatted date_str column (yyyy-MM-dd)
    df["date_str"] = df["trade_date"].dt.strftime("%Y-%m-%d")

    # 6. Convert numeric columns to proper numbers
    for col in ["open_price", "close_price", "volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 7. Drop exact duplicate rows
    df = df.drop_duplicates().reset_index(drop=True)

    print("\n=== AFTER CLEANING INFO ===")
    print(df.info())
    print("Cleaned shape:", df.shape)

    # 8. Save as cleaned.parquet
    CLEANED_PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CLEANED_PARQUET_PATH, index=False)
    print(f"Saved cleaned data to {CLEANED_PARQUET_PATH}")


if __name__ == "__main__":
    main()
