from MIDTERM_PROJECTS.data.clean_data import clean_data
from MIDTERM_PROJECTS.data.visualize_data import (plot_normalized_comparison, plot_correlation_heatmap)
from MIDTERM_PROJECTS.strategy.backtest import (run_single_backtest, run_portfolio_backtest)
from MIDTERM_PROJECTS.strategy.signals import (check_entry_signal,check_exit_signal)
from MIDTERM_PROJECTS.strategy.indicators import add_indicators
from MIDTERM_PROJECTS.strategy.performance import (calculate_cagr, calculate_max_drawdown, calculate_sharpe_ratio,
                                                   generate_report)
import yfinance as yf
import matplotlib.pyplot as plt
import os

# --- CONFIGURATION ---
# Thematic Portfolio: "AI & High Growth"
# TICKERS = ['AAPL', 'NFLX', 'QCOM', 'MU', 'ARM', 'DELL', 'VRT', 'ANET', 'CRWD', 'ORCL']
TICKERS = ['NVDA', 'AMD', 'MSFT', 'GOOGL', 'META', 'TSLA', 'PLTR', 'AVGO', 'AMZN', 'SMCI']
START_DATE = '2015-01-01'
END_DATE = '2025-10-01'

# Output directory for saving charts
IMAGE_DIR = 'images'
os.makedirs(IMAGE_DIR, exist_ok=True)


def main():

    # --- STEP 1: DATA ACQUISITION ---
    print("\n" + "=" * 50)
    print("STEP 1: FETCHING & CLEANING DATA")
    print("=" * 50)

    # Fetch data using the processor module
    data_dict = clean_data(TICKERS, START_DATE, END_DATE)

    # Safety check: Stop if no data was found
    if not data_dict:
        print("Error: No data retrieved. Please check your internet or ticker symbols.")
        return

    # --- STEP 2: MARKET VISUALIZATION ---
    print("\n" + "=" * 50)
    print("STEP 2: MARKET OVERVIEW CHARTS")
    print("=" * 50)

    print(">> Generating Normalized Comparison Chart...")
    plot_normalized_comparison(data_dict, save_path=f'{IMAGE_DIR}/market_comparison.png')

    print(">> Generating Correlation Heatmap...")
    plot_correlation_heatmap(data_dict, save_path=f'{IMAGE_DIR}/correlation_heatmap.png')

    # --- STEP 3: STRATEGY BACKTEST ---
    print("\n" + "=" * 50)
    print("STEP 3: RUNNING STRATEGY SIMULATION")
    print("=" * 50)

    portfolio_results = run_portfolio_backtest(data_dict)

    spy = yf.download('SPY', start=START_DATE, end=END_DATE, auto_adjust= False)['Adj Close']

    spy = spy.reindex(portfolio_results.index).ffill()

    initial_capital = portfolio_results['TOTAL'].iloc[0]
    spy_normalized = (spy / spy.iloc[0]) * initial_capital

    plt.figure(figsize=(12, 6))
    plt.plot(portfolio_results.index, portfolio_results['TOTAL'],
             label='AI Strategy', color='green', linewidth=2)
    plt.plot(spy_normalized.index, spy_normalized,
             label='S&P 500 (Benchmark)', color='gray', linestyle='--', alpha=0.7)

    plt.title('Strategy Performance vs. Benchmark', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Total Equity ($)')
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)

    save_path = f'{IMAGE_DIR}/strategy_result.png'
    plt.savefig(save_path, dpi=300)
    print(f"-> Strategy Result Chart saved to: {save_path}")

    # --- STEP 4: PERFORMANCE METRICS ---
    print("\n" + "=" * 50)
    print("STEP 4: FINAL PERFORMANCE REPORT")
    print("=" * 50)

    # Calculate metrics (CAGR, Sharpe, Drawdown)
    metrics = generate_report(portfolio_results['TOTAL'])

    # Print table
    print(f"{'METRIC':<20} | {'VALUE':<15}")
    print("-" * 40)
    for key, value in metrics.items():
        print(f"{key:<20} | {value:<15}")
    print("-" * 40)


if __name__ == "__main__":
    main()