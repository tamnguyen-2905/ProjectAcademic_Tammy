import pandas as pd
import numpy as np
from MIDTERM_PROJECTS.strategy.signals import (check_entry_signal,check_exit_signal)
from MIDTERM_PROJECTS.strategy.indicators import add_indicators


def run_single_backtest(df, fund=1000, rsi_buy=40, trailing_stop=0.10): # instead stop_loss = 0.07
    """
    Simulates trading on a single asset.
    Updated to support Hyperparameter Tuning via arguments.

    Args:
        df (pd.DataFrame): Data with indicators.
        fund (float): Initial capital.
        rsi_buy (int): RSI threshold for entry (Default: 40).
        trailing_stop (float) : (Default: 10).
    """
    df = add_indicators(df)
    cash = fund
    stock = 0
    highest_price = 0  # Track peak price
    equity = []

    for index, row in df.iterrows():
        price = row['close']
        ema = row.get('EMA_200')
        rsi = row.get('RSI')

        # BUY Logic
        if stock == 0 and not pd.isna(ema) and not pd.isna(rsi):
            if price > ema and rsi < rsi_buy:
                stock = cash / price
                cash = 0
                highest_price = price  # Initialize peak

        # SELL Logic (Trailing Stop)
        elif stock > 0:
            if price > highest_price:
                highest_price = price  # Update peak

            stop_price = highest_price * (1 - trailing_stop)

            if (rsi > 75) or (price < stop_price):
                cash = stock * price
                stock = 0
                highest_price = 0

        equity.append(cash + (stock * price))

    return pd.Series(equity, index=df.index[-len(equity):])


def run_portfolio_backtest(data_dict, capital_per_stock=1000):
    """
    Runs the backtest simulation for the entire portfolio.

    Returns:
        pd.DataFrame: Contains equity curves for individual assets and the 'TOTAL' portfolio.
    """
    portfolio_equity = pd.DataFrame()

    print(f"-> Starting simulation on {len(data_dict)} assets...")

    for ticker, df in data_dict.items():
        if df.empty: continue
        try:
            # Run independent simulation for each stock
            equity = run_single_backtest(df, capital_per_stock)
            portfolio_equity[ticker] = equity
        except Exception as e:
            print(f"Simulation failed for {ticker}: {e}")

    # Handle missing data (Forward Fill) to ensure summation works
    portfolio_equity = portfolio_equity.fillna(capital_per_stock)

    # Calculate Total Portfolio Value
    portfolio_equity['TOTAL'] = portfolio_equity.sum(axis=1)

    print("-> Simulation completed.")
    return portfolio_equity