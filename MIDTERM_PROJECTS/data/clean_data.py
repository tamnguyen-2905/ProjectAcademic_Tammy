import yfinance as yf
import pandas as pd
import numpy as np
import os

def clean_data(tickers, start_date, end_date):
    """
    Downloads and cleans historical stock data for a list of tickers.

    This function performs the following operations:
    1. Downloads raw data from Yahoo Finance.
    2. Flattens MultiIndex columns (if applicable).
    3. Validates data logic (e.g., High >= Low, Volume >= 0).
    4. Standardizes column names to lowercase (open, high, low, close, volume).
    5. Handles missing values using Last Observation Carried Forward (LOCF).
    6. Flags extreme volatility events (Fat Tail Analysis).

    Args:
        tickers (list or str): A single ticker symbol or a list of symbols (e.g., ['SPY', 'NVDA']).
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
        dict: A dictionary where keys are ticker symbols and values are cleaned pandas DataFrames.
    """

    processed_data = {}

    # Ensure input is a list
    if isinstance(tickers, str):
        tickers = [tickers]

    for ticker in tickers:
        print(f"\n{'=' * 40}")
        print(f"Processing Asset: {ticker}")
        print(f"{'=' * 40}")

        try:
            # 1. Download raw data
            df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)

            if df.empty:
                print(f"Warning: No data found for {ticker}. Skipping...")
                continue

            # 2. Handle MultiIndex (Flatten Columns)
            # yfinance often returns MultiIndex columns (Ticker, Price Type). We extract the Price Type.
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # 3. Logical Consistency Checks (Data Integrity)
            # Rule A: Volume must be non-negative
            mask_vol = df['Volume'] >= 0

            # Rule B: High price must be greater than or equal to Low price
            mask_hl = df['High'] >= df['Low']

            # Rule C: Open and Close must be within High-Low range (with tolerance for float precision)
            epsilon = 1e-4
            mask_rng_close = (df['Close'] <= df['High'] + epsilon) & (df['Close'] >= df['Low'] - epsilon)
            mask_rng_open = (df['Open'] <= df['High'] + epsilon) & (df['Open'] >= df['Low'] - epsilon)

            # Combine all validity masks
            valid_rows = mask_vol & mask_hl & mask_rng_close & mask_rng_open

            invalid_count = len(df) - valid_rows.sum()
            if invalid_count > 0:
                print(f"-> Integrity Check: Detected {invalid_count} rows with logical errors.")
                print('-> Action: Removing illogical data points.')
                df = df[valid_rows]
            else:
                print('-> Integrity Check: Passed. No illogical data found.')

            # 4. Standardize Column Names
            df = df.rename(columns={
                'Open': 'open', 'Adj Close': 'close', 'High': 'high', 'Low': 'low', 'Volume': 'volume'
            })

            # 5. Handle Missing Values
            # Use Forward Fill (LOCF) to maintain time-series continuity
            df = df.ffill()
            df = df.dropna()

            # 6. Fat Tail Analysis (Extreme Volatility Check)
            # Flag daily returns > 20% for manual review (potential M&A, earnings, or data error)
            daily_ret = df['close'].pct_change().abs()
            extreme_moves = daily_ret[daily_ret > 0.20]

            if not extreme_moves.empty:
                print(f"-> ALERT: Detected {len(extreme_moves)} days with extreme volatility (> 20%).")
                # print(extreme_moves.tail(3))

            # 8. Liquidity Check
            zero_vol_count = (df['volume'] == 0).sum()
            if zero_vol_count > 0:
                print(f"-> Note: Detected {zero_vol_count} trading days with Zero Volume (Illiquid).")

            # Store processed dataframe
            processed_data[ticker] = df
            print(f"-> Success. Final dataset shape: {df.shape}")

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    return processed_data


def save_data(data_dict):
    folder_name = 'cleaned data'
    os.makedirs(folder_name, exist_ok=True)

    for ticker, df in data_dict.items():
        file_path = os.path.join(folder_name, f"{ticker}.csv")
        df.to_csv(file_path)

my_tickers = ['NVDA', 'AMD', 'MSFT', 'GOOGL', 'META', 'TSLA', 'PLTR', 'AVGO', 'AMZN', 'SMCI']
start = '2015-01-01'
end = '2025-10-01'
cleaned_results = clean_data(my_tickers, start, end)
save_data(cleaned_results)