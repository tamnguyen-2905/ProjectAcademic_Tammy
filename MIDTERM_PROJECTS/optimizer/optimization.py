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
    print("\n" + "=" * 80)
    print("FULL GRID SEARCH: RSI BUY/SELL & TRAILING STOP")
    print("=" * 80)

    rsi_buy_options = [30, 35, 40]
    rsi_sell_options = [70, 75, 80]
    trail_options = [0.10, 0.12, 0.15]

    print(f"{'BUY':<4} | {'SELL':<4} | {'TRAIL':<5} | {'TRAIN SHARPE':<12} | {'TEST SHARPE':<12} | {'STATUS'}")
    print("-" * 70)

    best_score = -999
    best_params = None

    for r_buy in rsi_buy_options:
        for r_sell in rsi_sell_options:
            for trail in trail_options:

                if r_buy >= r_sell: continue

                train_scores, test_scores = [], []

                for ticker, df in data_dict.items():
                    if len(df) < 100: continue
                    train, test = split_data(df)

                    res_train = run_single_backtest(train, rsi_buy=r_buy, rsi_sell=r_sell, trailing_stop=trail)
                    res_test = run_single_backtest(test, rsi_buy=r_buy, rsi_sell=r_sell, trailing_stop=trail)

                    train_scores.append(calculate_sharpe(res_train))
                    test_scores.append(calculate_sharpe(res_test))

                avg_train = np.mean(train_scores) if train_scores else 0
                avg_test = np.mean(test_scores) if test_scores else 0

                status = "OVERFIT" if (avg_train > 1.2 and avg_test > 0.5) else "OK"
                print(
                    f"{r_buy:<4} | {r_sell:<4} | {trail * 100:<3.0f}%  | {avg_train:<12.2f} | {avg_test:<12.2f} | {status}")

                if avg_train > best_score and avg_test > 0.5:
                    best_score = avg_train
                    best_params = (r_buy, r_sell, trail)

    print("-" * 70)
    if best_params:
        print(f"RECOMMENDED: RSI_BUY={best_params[0]}, RSI_SELL={best_params[1]}, TRAILING={best_params[2]}")

from MIDTERM_PROJECTS.data.clean_data import clean_data

# TICKERS = ['AAPL', 'NFLX', 'QCOM', 'MU', 'ARM', 'DELL', 'VRT', 'ANET', 'CRWD', 'ORCL']
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