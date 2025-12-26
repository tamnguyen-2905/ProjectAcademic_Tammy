import pandas as pd
import numpy as np
from MIDTERM_PROJECTS.strategy.backtest import run_single_backtest

def split_data(df, train_ratio=0.8):
    """Split data chronologically (80% Train, 20% Test)"""
    n = int(len(df) * train_ratio)
    return df.iloc[:n], df.iloc[n:]


def calculate_sharpe(equity_series):
    """Calculate Annualized Sharpe Ratio"""
    if equity_series.empty: return 0
    ret = equity_series.pct_change().dropna()
    if ret.std() == 0: return 0
    return (ret.mean() / ret.std()) * np.sqrt(252)


def run_grid_search(data_dict):
    """
    Grid Search for Trailing Stop Optimization.
    """
    print("\n" + "=" * 60)
    print("GRID SEARCH: TRAILING STOP OPTIMIZATION (80/20 SPLIT)")
    print("=" * 60)

    # Grid Parameters
    rsi_options = [30, 35, 40]
    trail_options = [0.05, 0.08, 0.10, 0.12, 0.15]  # 5% to 15%

    print(f"{'RSI':<5} | {'TRAIL':<6} | {'TRAIN SHARPE':<12} | {'TEST SHARPE':<12} | {'STATUS'}")
    print("-" * 60)

    best_score = -999
    best_params = None

    for rsi in rsi_options:
        for trail in trail_options:
            train_scores, test_scores = [], []

            for ticker, df in data_dict.items():
                if len(df) < 100: continue
                train, test = split_data(df)

                # Run Backtest
                res_train = run_single_backtest(train, rsi_buy=rsi, trailing_stop=trail)
                res_test = run_single_backtest(test, rsi_buy=rsi, trailing_stop=trail)

                train_scores.append(calculate_sharpe(res_train))
                test_scores.append(calculate_sharpe(res_test))

            avg_train = np.mean(train_scores) if train_scores else 0
            avg_test = np.mean(test_scores) if test_scores else 0

            # Robustness Check
            status = "OK"
            if avg_train > 1.5 and avg_test < 0.5:
                status = "OVERFIT"
            elif avg_test < 0:
                status = "LOSS"

            print(f"{rsi:<5} | {trail * 100:<4.0f}% | {avg_train:<12.2f} | {avg_test:<12.2f} | {status}")

            if avg_train > best_score and avg_test > 0.5:
                best_score = avg_train
                best_params = (rsi, trail)

    print("-" * 60)
    if best_params:
        print(f"RECOMMENDED: RSI={best_params[0]}, TRAILING_STOP={best_params[1]}")
    else:
        print("RECOMMENDED: Default Settings (No robust params found).")

from MIDTERM_PROJECTS.data.clean_data import clean_data

TICKERS = ['NVDA', 'AMD', 'MSFT', 'GOOGL', 'META', 'TSLA', 'PLTR', 'AVGO', 'AMZN', 'SMCI']
START = '2015-01-01'
END = '2025-10-01'


def main():
    data = clean_data(TICKERS, START, END)
    if data:
        run_grid_search(data)
    else:
        print("Error: No data available for optimization.")


if __name__ == "__main__":
    main()