#!/usr/bin/env python3
"""
Nasdaq Advanced Charting Scraper
--------------------------------
Scrapes historical OHLCV data from the unofficial Nasdaq Advanced Charting API.
Provides command-line options to customize ticker, start date, end date, and output files.
"""

import argparse
import datetime
import json
import os
import sys
import pandas as pd
import requests

# Nasdaq requires proper headers to bypass simple anti-bot checks.
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.nasdaq.com",
    "Referer": "https://www.nasdaq.com/",
}

def clean_and_parse_data(raw_data):
    """
    Cleans the raw JSON response from Nasdaq's chart API and parses it into a list of dicts.
    
    Args:
        raw_data (dict): The JSON response dict from api.nasdaq.com.
        
    Returns:
        list[dict]: A list of cleaned data records.
    """
    if not raw_data or "data" not in raw_data or raw_data["data"] is None:
        raise ValueError("Invalid response payload from Nasdaq API. No data found.")
        
    chart_data = raw_data["data"].get("chart")
    if not chart_data:
        raise ValueError("No charting data ('chart' key) found in the Nasdaq response.")
        
    cleaned_records = []
    
    for point in chart_data:
        # The API nests the actual data inside 'z'
        details = point.get("z", {})
        if not details:
            continue
            
        try:
            # Clean date format: M/D/YYYY -> YYYY-MM-DD
            raw_date = details.get("dateTime")
            parsed_date = datetime.datetime.strptime(raw_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            try:
                # In case it is in %d/%m/%Y or another format
                parsed_date = datetime.datetime.strptime(raw_date, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                # Fallback to raw date if parsing fails
                parsed_date = raw_date
                
        try:
            # Clean and convert numeric fields
            open_val = float(details.get("open", "").replace(",", "")) if details.get("open") else None
            high_val = float(details.get("high", "").replace(",", "")) if details.get("high") else None
            low_val = float(details.get("low", "").replace(",", "")) if details.get("low") else None
            close_val = float(details.get("close", "").replace(",", "")) if details.get("close") else None
            volume_val = int(details.get("volume", "").replace(",", "")) if details.get("volume") else None
            price_val = float(details.get("value", "").replace(",", "")) if details.get("value") else None
            
            cleaned_records.append({
                "Date": parsed_date,
                "Open": open_val,
                "High": high_val,
                "Low": low_val,
                "Close": close_val,
                "Volume": volume_val,
                "Price": price_val
            })
        except Exception as e:
            # Skip corrupted rows but print warning
            print(f"Warning: Skipping data point on date {raw_date} due to parsing error: {e}", file=sys.stderr)
            
    return cleaned_records

def fetch_nasdaq_chart_data(ticker, start_date, end_date):
    """
    Sends request to Nasdaq advanced charting API endpoint.
    
    Args:
        ticker (str): Stock ticker symbol.
        start_date (str): Start date in YYYY-MM-DD.
        end_date (str): End date in YYYY-MM-DD.
        
    Returns:
        dict: Raw JSON response from the API.
    """
    url = f"https://api.nasdaq.com/api/quote/{ticker.upper()}/chart"
    params = {
        "assetclass": "stocks",
        "fromdate": start_date,
        "todate": end_date
    }
    
    print(f"Fetching data for {ticker.upper()} from {start_date} to {end_date}...")
    response = requests.get(url, headers=DEFAULT_HEADERS, params=params, timeout=15)
    
    if response.status_code != 200:
        raise ConnectionError(f"HTTP error {response.status_code} received from Nasdaq API. Details: {response.text[:200]}")
        
    data = response.json()
    
    # Check if API returned an internal error
    status_info = data.get("status", {})
    if status_info.get("rCode") != 200:
        error_msg = "; ".join([e.get("errorMessage", "") for e in status_info.get("bCodeMessage", [])])
        raise ValueError(f"Nasdaq API returned error status {status_info.get('rCode')}: {error_msg}")
        
    return data

def main():
    parser = argparse.ArgumentParser(description="Scrape stock dataset from Nasdaq advanced charting API.")
    parser.add_argument("--ticker", "-t", type=str, default="AAPL", help="Stock ticker symbol (default: AAPL)")
    parser.add_argument("--start-date", "-s", type=str, help="Start date in YYYY-MM-DD format (default: 5 years ago)")
    parser.add_argument("--end-date", "-e", type=str, help="End date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--output-prefix", "-o", type=str, help="Prefix/path for output files (default: <ticker>_nasdaq_dataset)")
    parser.add_argument("--format", "-f", type=str, choices=["csv", "json", "both"], default="both", 
                        help="Output format: csv, json, or both (default: both)")
    
    args = parser.parse_args()
    
    # Set default dates if not provided
    end_dt = datetime.date.today()
    if args.end_date:
        try:
            end_dt = datetime.datetime.strptime(args.end_date, "%Y-%m-%d").date()
        except ValueError:
            print("Error: End date must be in YYYY-MM-DD format.", file=sys.stderr)
            sys.exit(1)
            
    if args.start_date:
        try:
            start_dt = datetime.datetime.strptime(args.start_date, "%Y-%m-%d").date()
        except ValueError:
            print("Error: Start date must be in YYYY-MM-DD format.", file=sys.stderr)
            sys.exit(1)
    else:
        # Default to 5 years ago
        start_dt = end_dt - datetime.timedelta(days=5*365)
        
    ticker = args.ticker.upper()
    start_str = start_dt.strftime("%Y-%m-%d")
    end_str = end_dt.strftime("%Y-%m-%d")
    output_prefix = args.output_prefix
    if not output_prefix:
        os.makedirs("downloads", exist_ok=True)
        output_prefix = os.path.join("downloads", f"{ticker.lower()}_nasdaq_dataset")
    
    try:
        # Fetch and parse
        raw_response = fetch_nasdaq_chart_data(ticker, start_str, end_str)
        cleaned_records = clean_and_parse_data(raw_response)
        
        if not cleaned_records:
            print("No records retrieved. Exiting.", file=sys.stderr)
            sys.exit(1)
            
        # Create DataFrame
        df = pd.DataFrame(cleaned_records)
        # Ensure correct column ordering
        df = df[["Date", "Open", "High", "Low", "Close", "Volume", "Price"]]
        
        # Sort by Date ascending
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by="Date").reset_index(drop=True)
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        
        # Output files
        saved_files = []
        if args.format in ["csv", "both"]:
            csv_path = f"{output_prefix}.csv"
            df.to_csv(csv_path, index=False)
            saved_files.append(csv_path)
            
        if args.format in ["json", "both"]:
            json_path = f"{output_prefix}.json"
            # Save as pretty JSON records
            with open(json_path, "w") as f:
                json.dump(cleaned_records, f, indent=2)
            saved_files.append(json_path)
            
        # Display dataset info
        print("\nSuccess! Dataset generated successfully.")
        print(f"Saved dataset file(s): {', '.join(saved_files)}")
        print("\nDataset Summary:")
        print(f"  Ticker: {ticker}")
        print(f"  Date Range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
        print(f"  Total Data Points: {len(df)}")
        print("\nFirst 5 Rows:")
        print(df.head())
        print("\nLast 5 Rows:")
        print(df.tail())
        
    except Exception as e:
        print(f"\nError: Failed to generate dataset: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
