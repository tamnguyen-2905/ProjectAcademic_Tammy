# --- STRATEGY CONFIGURATION ---
RSI_OVERSOLD = 40  # Entry Threshold (Buy on Pullback)
RSI_OVERBOUGHT = 75  # Exit Threshold (Take Profit)
STOP_LOSS_PCT = 0.07  # Hard Stop Loss (7%)


def check_entry_signal(price, ema, rsi):
    """
    Checks conditions for a LONG entry.

    Strategy Logic: Trend Following + Mean Reversion Pullback
    1. Trend: Price must be above EMA 200.
    2. Setup: RSI must be below 40 (Short-term oversold).

    Returns:
        bool: True if entry conditions are met.
    """
    # Validation: Ensure indicators exist
    if price is None or ema is None or rsi is None:
        return False

    is_uptrend = price > ema
    is_pullback = rsi < RSI_OVERSOLD

    return is_uptrend and is_pullback


def check_exit_signal(price, rsi, entry_price):
    """
    Checks conditions for closing a position.

    Exit Logic:
    1. Take Profit: RSI becomes overbought (> 75).
    2. Stop Loss: Price drops 7% below entry price.

    Returns:
        bool: True if exit conditions are met.
    """
    if entry_price == 0: return False

    # 1. Take Profit (RSI Overheated)
    take_profit = rsi > RSI_OVERBOUGHT

    # 2. Stop Loss (Risk Management)
    stop_loss = price < entry_price * (1 - STOP_LOSS_PCT)

    return take_profit or stop_loss