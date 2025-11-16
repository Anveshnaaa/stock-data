from pathlib import Path

import pandas as pd
import streamlit as st

# Paths to your aggregate parquet files
AGG1_PATH = Path("data/processed/agg1.parquet")
AGG2_PATH = Path("data/processed/agg2.parquet")


@st.cache_data
def load_aggregates():
    """
    Load aggregation tables from parquet files and detect key columns.
    """
    agg1 = pd.read_parquet(AGG1_PATH)
    agg2 = pd.read_parquet(AGG2_PATH)

    # We know from make_aggs.py:
    # agg1 columns: trade_date, ticker, avg_close
    # agg2 columns: ticker, avg_volume

    # Ensure trade_date is datetime
    agg1["trade_date"] = pd.to_datetime(agg1["trade_date"], errors="coerce")

    return agg1, agg2


def main():
    st.title("📈 Stock Market – Cleaned Data Visualizations")
    st.write(
        "This app uses cleaned stock market data and precomputed aggregations "
        "to show daily average closing prices and average volume by ticker."
    )

    # Load aggregated data
    agg1, agg2 = load_aggregates()

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")

    # Date range filter
    min_date = agg1["trade_date"].min().date()
    max_date = agg1["trade_date"].max().date()

    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Ticker filter
    tickers = sorted(agg1["ticker"].dropna().unique().tolist())
    default_tickers = tickers[:3] if len(tickers) >= 3 else tickers
    selected_tickers = st.sidebar.multiselect(
        "Select ticker(s)",
        options=tickers,
        default=default_tickers,
    )

    # --- Apply filters to agg1 (daily avg close) ---
    filtered = agg1.copy()

    # Date range filter logic
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        filtered = filtered[
            (filtered["trade_date"].dt.date >= start)
            & (filtered["trade_date"].dt.date <= end)
        ]

    # Ticker filter logic
    if selected_tickers:
        filtered = filtered[filtered["ticker"].isin(selected_tickers)]

    # --- Chart 1: Daily avg close by ticker ---
    st.subheader("📉 Daily Average Closing Price by Ticker")
    st.write("Line chart of `avg_close` over time for the selected ticker(s).")

    if filtered.empty:
        st.warning("No data available for the selected filters.")
    else:
        # Pivot so each ticker becomes a separate line
        pivot_df = filtered.pivot_table(
            index="trade_date", columns="ticker", values="avg_close"
        ).sort_index()

        st.line_chart(pivot_df)

    # --- Chart 2: Average volume by ticker ---
    st.subheader("📊 Average Volume by Ticker")
    st.write("Bar chart of `avg_volume` for the selected ticker(s).")

    # Filter agg2 based on selected tickers
    if selected_tickers:
        agg2_filtered = agg2[agg2["ticker"].isin(selected_tickers)]
    else:
        agg2_filtered = agg2

    if agg2_filtered.empty:
        st.warning("No volume data available for selected ticker(s).")
    else:
        # Set ticker as index so Streamlit uses it as x-axis labels
        volume_series = agg2_filtered.set_index("ticker")["avg_volume"]
        st.bar_chart(volume_series)

    st.markdown("---")
    st.caption("Built with cleaned.parquet, agg1.parquet, agg2.parquet and Streamlit.")


if __name__ == "__main__":
    main()
