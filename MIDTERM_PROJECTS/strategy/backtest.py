import pandas as pd
import numpy as np
from MIDTERM_PROJECTS.strategy.signals import (check_entry_signal,check_exit_signal)
from MIDTERM_PROJECTS.strategy.indicators import add_indicators


def run_single_backtest(df, initial_capital=1000):
    """
    Simulates the trading strategy on a single asset.

    Args:
        df (pd.DataFrame): Historical data.
        initial_capital (float): Starting cash.

    Returns:
        pd.Series: The Equity Curve (Total Asset Value over time).
    """
    # 1. Pre-calculate indicators
    df = add_indicators(df)

    # 2. Initialize State
    cash = initial_capital
    position = 0  # Number of shares held
    entry_price = 0  # Average cost basis
    equity_curve = []  # Track value over time

    # 3. Time-Stepping Simulation Loop
    for index, row in df.iterrows():
        price = row['close']

        # Use .get() to safely handle NaN values at the start of data
        ema = row.get('EMA_200')
        rsi = row.get('RSI')

        # Skip simulation if indicators are not ready (NaN)
        if pd.isna(ema) or pd.isna(rsi):
            equity_curve.append(cash)
            continue

        # --- EXECUTION LOGIC ---

        # Scenario: Holding Cash -> Look to BUY
        if position == 0:
            if check_entry_signal(price, ema, rsi):
                position = cash / price  # All-in execution
                entry_price = price
                cash = 0

        # Scenario: Holding Stock -> Look to SELL
        elif position > 0:
            if check_exit_signal(price, rsi, entry_price):
                cash = position * price  # Liquidate position
                position = 0
                entry_price = 0

        # --- MARK TO MARKET CALCULATION ---
        # Current Value = Cash + (Shares * Current Price)
        current_equity = cash + (position * price)
        equity_curve.append(current_equity)

    # Return Series with matching index dates
    return pd.Series(equity_curve, index=df.index[-len(equity_curve):])


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