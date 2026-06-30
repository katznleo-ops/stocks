#!/usr/bin/env python3
"""
AAPL Stock Data Analysis Script
------------------------------
Reads AAPL historical stock data from the downloads/ directory, performs standard
financial analysis (OHLCV statistics, moving averages, returns, volatility),
outputs a summary to stdout, and saves an analysis report.
"""

import os
import sys
import pandas as pd

def run_analysis(csv_path, output_report_path):
    """
    Performs data analysis on the given stock CSV file and saves a text report.
    """
    if not os.path.exists(csv_path):
        print(f"Error: Dataset file not found at {csv_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)

    # Ensure Date is parsed and sorted chronologically
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(by="Date").reset_index(drop=True)

    total_days = len(df)
    if total_days == 0:
        print("Error: The dataset is empty.", file=sys.stderr)
        sys.exit(1)

    # 1. Price Calculations
    min_close = df["Close"].min()
    min_close_date = df.loc[df["Close"].idxmin(), "Date"].strftime("%Y-%m-%d")
    max_close = df["Close"].max()
    max_close_date = df.loc[df["Close"].idxmax(), "Date"].strftime("%Y-%m-%d")
    avg_close = df["Close"].mean()
    latest_close = df["Close"].iloc[-1]
    latest_date = df["Date"].iloc[-1].strftime("%Y-%m-%d")
    earliest_date = df["Date"].iloc[0].strftime("%Y-%m-%d")

    # 2. Volume Calculations
    avg_volume = df["Volume"].mean()
    max_volume = df["Volume"].max()
    max_vol_date = df.loc[df["Volume"].idxmax(), "Date"].strftime("%Y-%m-%d")

    # 3. Simple Moving Averages (SMA)
    df["SMA_50"] = df["Close"].rolling(window=50).mean()
    df["SMA_200"] = df["Close"].rolling(window=200).mean()

    # 4. Daily Returns and Volatility
    df["Daily_Return"] = df["Close"].pct_change()
    avg_daily_return = df["Daily_Return"].mean()
    volatility = df["Daily_Return"].std()  # Daily volatility

    best_day_idx = df["Daily_Return"].idxmax()
    best_day_pct = df.loc[best_day_idx, "Daily_Return"] * 100
    best_day_date = df.loc[best_day_idx, "Date"].strftime("%Y-%m-%d")

    worst_day_idx = df["Daily_Return"].idxmin()
    worst_day_pct = df.loc[worst_day_idx, "Daily_Return"] * 100
    worst_day_date = df.loc[worst_day_idx, "Date"].strftime("%Y-%m-%d")

    # Format the report string
    ticker = os.path.basename(csv_path).split("_")[0].upper()
    report = []
    report.append("==================================================")
    report.append(f"          {ticker} STOCK DATA ANALYSIS REPORT         ")
    report.append("==================================================")
    report.append(f"Analysis generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Data Date Range:       {earliest_date} to {latest_date}")
    report.append(f"Total Trading Days:    {total_days}")
    report.append("--------------------------------------------------")
    report.append("1. CLOSE PRICE STATISTICS:")
    report.append(f"  * Latest Close:      ${latest_close:.2f} ({latest_date})")
    report.append(f"  * Average Close:     ${avg_close:.2f}")
    report.append(f"  * Highest Close:     ${max_close:.2f} (on {max_close_date})")
    report.append(f"  * Lowest Close:      ${min_close:.2f} (on {min_close_date})")
    report.append("--------------------------------------------------")
    report.append("2. TRADING VOLUME STATISTICS:")
    report.append(f"  * Average Volume:    {avg_volume:,.0f} shares")
    report.append(f"  * Peak Volume:       {max_volume:,.0f} shares (on {max_vol_date})")
    report.append("--------------------------------------------------")
    report.append("3. DAILY RETURN & VOLATILITY:")
    report.append(f"  * Average Return:    {avg_daily_return * 100:+.4f}% per day")
    report.append(f"  * Volatility (Std):  {volatility * 100:.4f}% daily")
    report.append(f"  * Best Day Gain:     {best_day_pct:+.2f}% (on {best_day_date})")
    report.append(f"  * Worst Day Loss:    {worst_day_pct:+.2f}% (on {worst_day_date})")
    report.append("--------------------------------------------------")
    report.append("4. SIMPLE MOVING AVERAGES (SMA) - LATEST VALUES:")
    sma_50_val = df["SMA_50"].iloc[-1]
    sma_200_val = df["SMA_200"].iloc[-1]
    report.append(f"  * 50-day SMA:        ${sma_50_val:.2f}" if not pd.isna(sma_50_val) else "  * 50-day SMA:        N/A (insufficient data)")
    report.append(f"  * 200-day SMA:       ${sma_200_val:.2f}" if not pd.isna(sma_200_val) else "  * 200-day SMA:       N/A (insufficient data)")
    report.append("==================================================")

    report_text = "\n".join(report)

    # Print to console
    print("\n" + report_text + "\n")

    # Write report to file
    os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
    with open(output_report_path, "w") as f:
        f.write(report_text)
    print(f"Saved analysis report to: {output_report_path}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    downloads_dir = os.path.join(project_root, "downloads")
    
    if os.path.exists(downloads_dir):
        for filename in os.listdir(downloads_dir):
            if filename.endswith("_nasdaq_dataset.csv"):
                ticker_symbol = filename.split("_")[0].lower()
                csv_file = os.path.join(downloads_dir, filename)
                report_file = os.path.join(downloads_dir, f"{ticker_symbol}_analysis_report.txt")
                try:
                    run_analysis(csv_file, report_file)
                except Exception as e:
                    print(f"Error analyzing {ticker_symbol.upper()}: {e}", file=sys.stderr)
