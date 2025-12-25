import pandas as pd
import numpy as np


def add_indicators(df):
    """
    Calculates and appends technical indicators to the DataFrame.

    Indicators used:
    1. EMA (200-period): Used as a Trend Filter (Long-term trend).
    2. RSI (14-period): Used as a Momentum Indicator (Overbought/Oversold levels).

    Args:
        df (pd.DataFrame): DataFrame containing 'close' price column.

    Returns:
        pd.DataFrame: DataFrame with added 'EMA_200' and 'RSI' columns.
    """
    df = df.copy()

    # 1. Exponential Moving Average (EMA 200)
    # Logic: Determines the long-term trend direction.
    df['EMA_200'] = df['close'].ewm(span=200, adjust=False).mean()

    # 2. Relative Strength Index (RSI 14)
    # Calculation performed manually to avoid dependency on 'ta' library.
    delta = df['close'].diff()

    # Separate gains and losses
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

    # Calculate RS and RSI
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    return df