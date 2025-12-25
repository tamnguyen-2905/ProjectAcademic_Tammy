import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os

plt.style.use('ggplot')


def plot_normalized_comparison(data_dict, save_path=None):
    """
    Vẽ biểu đồ so sánh hiệu suất tương đối của các mã (Quy về mốc 100).
    Thích hợp để làm ảnh bìa cho GitHub.
    """
    plt.figure(figsize=(14, 8))

    # Danh sách các mã cần làm nổi bật (Key players)
    highlight_tickers = ['NVDA', 'SMCI', 'TSLA']

    for ticker, df in data_dict.items():
        if df.empty: continue

        # 1. Chuẩn hóa dữ liệu (Rebase to 100)
        # Giá ngày t / Giá ngày đầu tiên * 100
        first_price = df['close'].iloc[0]
        normalized_price = df['close'] / first_price * 100

        # 2. Vẽ biểu đồ
        if ticker in highlight_tickers:
            # Vẽ đậm các mã quan trọng
            plt.plot(normalized_price.index, normalized_price,
                     linewidth=2.5, label=f"{ticker} (Leader)")
        else:
            # Vẽ mờ các mã khác
            plt.plot(normalized_price.index, normalized_price,
                     linewidth=1, alpha=0.6, label=ticker)

    # 3. Trang trí
    plt.title('Relative Performance Comparison (Base = 100)', fontsize=16, fontweight='bold')
    plt.ylabel('Growth (%)', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.axhline(100, color='black', linestyle='--', alpha=0.5, linewidth=1)  # Đường gốc
    plt.legend(loc='upper left', fontsize=10, ncol=2)
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.tight_layout()

    # 4. Lưu ảnh (nếu có yêu cầu)
    if save_path:
        # Tạo thư mục images nếu chưa có
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300)
        print(f"Chart saved to: {save_path}")

    plt.show()


def plot_individual_health_check(data_dict):
    """
    Vẽ Dashboard kiểm tra sức khỏe dữ liệu cho TỪNG mã.
    Bao gồm: Giá, Khối lượng và cảnh báo biến động mạnh (>20%).
    """
    for ticker, df in data_dict.items():
        if df.empty: continue

        # Tạo 2 biểu đồ con (Giá ở trên, Volume ở dưới)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                       gridspec_kw={'height_ratios': [3, 1]})

        # --- BIỂU ĐỒ 1: GIÁ (PRICE) ---
        ax1.plot(df.index, df['close'], color='#2c3e50', linewidth=1.5, label='Close Price')

        # Highlight: Tìm những ngày biến động > 20% (Dấu hiệu bất thường hoặc tin sốc)
        daily_ret = df['close'].pct_change().abs()
        extreme_mask = daily_ret > 0.20

        if extreme_mask.any():
            extreme_points = df[extreme_mask]
            ax1.scatter(extreme_points.index, extreme_points['close'],
                        color='red', s=50, zorder=5, label='Extreme Volatility (>20%)')

            # Ghi chú ngày lên biểu đồ
            for date, row in extreme_points.iterrows():
                ax1.annotate(f"{date.strftime('%Y-%m-%d')}",
                             (date, row['close']),
                             xytext=(10, 10), textcoords='offset points',
                             fontsize=8, color='red', arrowprops=dict(arrowstyle="->", color='red'))

        ax1.set_title(f'{ticker} - Data Health Check', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)

        # --- BIỂU ĐỒ 2: KHỐI LƯỢNG (VOLUME) ---
        # Tô màu xanh (Tăng) / Đỏ (Giảm)
        colors = ['#27ae60' if r['close'] >= r['open'] else '#c0392b' for i, r in df.iterrows()]
        ax2.bar(df.index, df['volume'], color=colors, width=1.0)
        ax2.set_ylabel('Volume')
        ax2.set_xlabel('Date')
        ax2.grid(True, alpha=0.3)

        # Định dạng ngày tháng trục hoành
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        plt.tight_layout()
        plt.show()
        print(f"-> Displayed health check for {ticker}")

