import numpy as np
import pandas as pd


def calculate_cagr(equity_series):
    """Calculates Compound Annual Growth Rate (CAGR)."""
    if equity_series.empty: return 0

    days = (equity_series.index[-1] - equity_series.index[0]).days
    if days == 0: return 0
    years = days / 365.25

    start_val = equity_series.iloc[0]
    end_val = equity_series.iloc[-1]

    # Formula: (End/Start)^(1/years) - 1
    return (end_val / start_val) ** (1 / years) - 1


def calculate_max_drawdown(equity_series):
    """Calculates Maximum Drawdown (Deepest decline from peak)."""
    rolling_max = equity_series.cummax()
    drawdown = (equity_series - rolling_max) / rolling_max
    return drawdown.min()


def calculate_sharpe_ratio(equity_series, risk_free_rate=0.0):
    """
    Calculates Annualized Sharpe Ratio.
    Measure of risk-adjusted return.
    """
    daily_returns = equity_series.pct_change().dropna()

    mean_ret = daily_returns.mean()
    std_ret = daily_returns.std()

    if std_ret == 0: return 0

    # Annualize: Daily Sharpe * sqrt(252 trading days)
    sharpe = ((mean_ret - risk_free_rate / 252) / std_ret) * np.sqrt(252)
    return sharpe


def generate_report(equity_series):
    """
    Generates a dictionary of key performance metrics for reporting.
    """
    if equity_series.empty:
        return {"Error": "No data available for analysis"}

    total_return = (equity_series.iloc[-1] - equity_series.iloc[0]) / equity_series.iloc[0]

    return {
        "Initial Capital": f"${equity_series.iloc[0]:,.2f}",
        "Final Equity": f"${equity_series.iloc[-1]:,.2f}",
        "Total Return": f"{total_return * 100:.2f}%",
        "CAGR": f"{calculate_cagr(equity_series) * 100:.2f}%",
        "Max Drawdown": f"{calculate_max_drawdown(equity_series) * 100:.2f}%",
        "Sharpe Ratio": f"{calculate_sharpe_ratio(equity_series):.2f}"
    }