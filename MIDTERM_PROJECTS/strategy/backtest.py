import pandas as pd
import numpy as np
from MIDTERM_PROJECTS.strategy.signals import (check_entry_signal,check_exit_signal)
from MIDTERM_PROJECTS.strategy.indicators import add_indicators


def run_single_backtest(df, fund=1000, rsi_buy=40, rsi_sell=75, trailing_stop=0.10):
    """
    Simulates the trading strategy on a single asset using Trailing Stop logic.

    Args:
        df (pd.DataFrame): Historical data.
        fund (float): Initial capital.
        rsi_buy (int): RSI threshold for entry (Optimization parameter).
        trailing_stop (float): Trailing stop percentage (Optimization parameter).

    Returns:
        pd.Series: Daily equity values over time.
    """
    # 1. Calculate Technical Indicators
    df = add_indicators(df)

    # 2. Initialize Portfolio State
    cash = fund
    stock = 0
    highest_price = 0  # Tracks the peak price for Trailing Stop
    equity = []

    # 3. Simulation Loop
    for index, row in df.iterrows():
        price = row['close']
        ema = row.get('EMA_200')
        rsi = row.get('RSI')

        # --- ENTRY LOGIC (BUY) ---
        if stock == 0:
            if check_entry_signal(price, ema, rsi, rsi_threshold=rsi_buy):
                stock = cash / price  # Buy All-in
                cash = 0
                highest_price = price  # Initialize peak price at entry

        # --- EXIT LOGIC (SELL) ---
        elif stock > 0:
            # Update the highest price seen during the trade
            if price > highest_price:
                highest_price = price

            # Check exit conditions (Take Profit or Trailing Stop)
            if check_exit_signal(price, rsi, highest_price,
                                 trailing_stop_pct=trailing_stop,
                                 rsi_sell_threshold=rsi_sell):
                cash = stock * price  # Liquidate position
                stock = 0
                highest_price = 0  # Reset peak

        # --- MARK TO MARKET ---
        # Calculate total asset value for the day
        current_equity = cash + (stock * price)
        equity.append(current_equity)

    # Return the Equity Curve aligned with dates
    return pd.Series(equity, index=df.index[-len(equity):])


def run_portfolio_backtest(data_dict, capital_per_stock=1000):
    """
    Executes the backtest across the entire portfolio.

    Args:
        data_dict (dict): Dictionary of DataFrames {Ticker: Data}.
        capital_per_stock (float): Capital allocated to each asset.

    Returns:
        pd.DataFrame: Equity curves for individual assets and the 'TOTAL' portfolio.
    """
    portfolio_equity = pd.DataFrame()
    print(f">> Executing Strategy (RSI < 40, Trailing Stop Mode)...")

    for ticker, df in data_dict.items():
        if df.empty: continue

        try:
            # Run simulation for the specific ticker
            # Note: You can pass optimized parameters here if needed
            result = run_single_backtest(df, fund=capital_per_stock)
            portfolio_equity[ticker] = result
        except Exception as e:
            print(f"Error backtesting {ticker}: {e}")

    # Handle missing data (Forward Fill) and sum up the portfolio
    portfolio_equity = portfolio_equity.ffill().fillna(capital_per_stock)
    portfolio_equity['TOTAL'] = portfolio_equity.sum(axis=1)

    return portfolio_equity