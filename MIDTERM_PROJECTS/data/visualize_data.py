import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
import os

plt.style.use('ggplot')


def plot_normalized_comparison(data_dict, save_path=None):
    """
    Plots the relative performance of assets rebased to 100.
    All assets are plotted uniformly without specific highlighting.

    Args:
        data_dict (dict): Dictionary containing processed DataFrames.
        save_path (str, optional): Path to save the image (e.g., 'images/comparison.png').
    """
    plt.figure(figsize=(14, 8))

    for ticker, df in data_dict.items():
        if df.empty: continue

        # 1. Normalize Data (Rebase to 100)
        # Formula: Price_t / Price_0 * 100
        first_price = df['close'].iloc[0]
        normalized_price = df['close'] / first_price * 100

        # 2. Plotting
        plt.plot(normalized_price.index, normalized_price,
                 linewidth=1.5, alpha=0.8, label=ticker)

    # 3. Chart Styling
    plt.title('Relative Performance Comparison (Base = 100)', fontsize=16, fontweight='bold')
    plt.ylabel('Growth (%)', fontsize=12)
    plt.xlabel('Date', fontsize=12)

    # Reference line at 100 (Break-even point)
    plt.axhline(100, color='black', linestyle='--', alpha=0.5, linewidth=1)

    plt.legend(loc='upper left', fontsize=10, ncol=2)
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.tight_layout()

    # 4. Save Image
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300)
        print(f"Chart saved to: {save_path}")

    plt.show()


def plot_individual_health_check(data_dict):
    """
    Plots a Data Health Check Dashboard for EACH asset.
    Includes: Price, Volume, and Extreme Volatility Alerts (>20%).
    """
    for ticker, df in data_dict.items():
        if df.empty: continue

        # Create subplots (Price on top, Volume on bottom)
        # height_ratios=[3, 1] means Price chart is 3x taller than Volume chart
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                       gridspec_kw={'height_ratios': [3, 1]})

        # --- CHART 1: PRICE ---
        ax1.plot(df.index, df['close'], color='#2c3e50', linewidth=1.5, label='Close Price')

        # Highlight: Detect days with > 20% volatility (Anomalies or News)
        daily_ret = df['close'].pct_change().abs()
        extreme_mask = daily_ret > 0.20

        if extreme_mask.any():
            extreme_points = df[extreme_mask]
            ax1.scatter(extreme_points.index, extreme_points['close'],
                        color='red', s=50, zorder=5, label='Extreme Volatility (>20%)')

            # Annotate specific dates
            for date, row in extreme_points.iterrows():
                ax1.annotate(f"{date.strftime('%Y-%m-%d')}",
                             (date, row['close']),
                             xytext=(10, 10), textcoords='offset points',
                             fontsize=8, color='red', arrowprops=dict(arrowstyle="->", color='red'))

        ax1.set_title(f'{ticker} - Data Health Check (Price & Volume)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)

        # --- CHART 2: VOLUME ---
        # Color: Green if Close >= Open, else Red
        colors = ['#27ae60' if r['close'] >= r['open'] else '#c0392b' for i, r in df.iterrows()]
        ax2.bar(df.index, df['volume'], color=colors, width=1.0)
        ax2.set_ylabel('Volume')
        ax2.set_xlabel('Date')
        ax2.grid(True, alpha=0.3)

        # Date Format (Year-Month)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        plt.tight_layout()
        plt.show()
        print(f"-> Displayed health check for {ticker}")


def plot_correlation_heatmap(data_dict, save_path=None):
    """
    Plots the Correlation Matrix based on daily returns.
    Useful for analyzing portfolio diversification and systematic risk.
    """
    # 1. Prepare Data: Combine Close Prices into a single DataFrame
    price_data = {}
    for ticker, df in data_dict.items():
        if not df.empty:
            price_data[ticker] = df['close']

    combined_df = pd.DataFrame(price_data)

    # 2. Calculate Correlation on Returns (Not Prices)
    # Prices are non-stationary, so correlation must be based on % change.
    returns_df = combined_df.pct_change().dropna()

    # 3. Compute Matrix
    corr_matrix = returns_df.corr()

    # 4. Plot Heatmap
    plt.figure(figsize=(10, 8))

    # Colormap: Red (High Positive Correlation) to Blue (Negative Correlation)
    sns.heatmap(corr_matrix,
                annot=True,  # Show numbers
                cmap='RdBu_r',  # Red-Blue reversed
                vmin=-1, vmax=1,  # Scale from -1 to 1
                fmt=".2f",  # 2 decimal places
                linewidths=0.5,  # Lines between cells
                square=True,  # Force square cells
                cbar_kws={"shrink": .75})

    plt.title('Daily Returns Correlation Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()

    # 5. Save Image
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300)
        print(f"Heatmap saved to: {save_path}")

    plt.show()