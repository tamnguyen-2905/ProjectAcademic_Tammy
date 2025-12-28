import pandas as pd


def check_entry_signal(price, ema, rsi, rsi_threshold=40):
    """
    Evaluates conditions for opening a LONG position.

    Strategy: Trend Following + Mean Reversion
    1. Trend Filter: Price must be above EMA 200 (Long-term Uptrend).
    2. Entry Trigger: RSI must be below the threshold (Buying the dip).

    Args:
        price (float): Current closing price.
        ema (float): Current EMA 200 value.
        rsi (float): Current RSI 14 value.
        rsi_threshold (int): The RSI level to trigger a buy (default: 40).

    Returns:
        bool: True if entry conditions are met, otherwise False.
    """
    # Validation: Ensure indicators are not NaN
    if pd.isna(ema) or pd.isna(rsi):
        return False

    is_uptrend = price > ema
    is_pullback = rsi < rsi_threshold

    return is_uptrend and is_pullback


def check_exit_signal(price, rsi, highest_price, trailing_stop_pct=0.10, rsi_sell_threshold=75):
    """
    Evaluates conditions for closing a position.

    Exit Logic:
    1. Take Profit: RSI becomes Overbought (> 75).
    2. Trailing Stop: Price drops by a specific percentage from the highest peak.

    Args:
        price (float): Current closing price.
        rsi (float): Current RSI 14 value.
        highest_price (float): The highest price reached since entry.
        trailing_stop_pct (float): Percentage drop to trigger exit (e.g., 0.10 for 10%).

    Returns:
        bool: True if exit conditions are met.
    """
    # 1. Take Profit (Momentum is overheated)
    take_profit = rsi > rsi_sell_threshold

    # 2. Trailing Stop (Protect profits / Limit downside)
    stop_price = highest_price * (1 - trailing_stop_pct)
    hit_trailing_stop = price < stop_price

    return take_profit or hit_trailing_stop