from MIDTERM_PROJECTS.data.clean_data import clean_data
from MIDTERM_PROJECTS.data.visualize_data import plot_normalized_comparison, plot_individual_health_check

# 1. Cấu hình
tickers = ['NVDA', 'MSFT', 'TSLA', 'PLTR']
start_date = '2023-01-01'
end_date = '2025-10-01'

# 2. Xử lý dữ liệu (Gọi hàm từ file data_processor.py)
print("--- STEP 1: PROCESSING DATA ---")
data_dict = clean_data(tickers, start_date, end_date)

# 3. Vẽ biểu đồ (Gọi hàm từ file visualization.py)
print("\n--- STEP 2: VISUALIZATION ---")

# Vẽ biểu đồ so sánh (để up lên GitHub)
plot_normalized_comparison(data_dict, save_path='images/comparison_chart.png')

# Soi chi tiết từng mã (để kiểm tra)
plot_individual_health_check(data_dict)