# main.py
import pandas as pd
from data_downloader import download_data
from backtest import run_momentum_strategy
from metrics import summary_metrics
import matplotlib.pyplot as plt

# Parameters
TICKERS = ["SPY", "QQQ", "IWM", "EEM", "EFA", "XLF", "HYG", "TLT", "XLE", "LQD", "XLV", "DIA", "GLD", "XLU", "JNK", "SOXL", "XLK", 
           "XBI", "ARKK", "UVXY", "FXI", "VEA", "EWZ", "VXX", "SH", "PSQ", "TQQQ", "SQQQ", "VOO", "IVV"]
START_DATE = "2010-01-01"
END_DATE = "2024-12-31"
TOP_N = 3
BENCHMARK = 'SPY'
REBALANCING_FREQ = '1M'

# Data download
print("Downloading data...")
price_data = download_data(TICKERS, start=START_DATE, end=END_DATE)
price_data.to_csv("etf_data.csv")

# Run the strategy
print("Running the momentum strategy...")
portfolio, weights = run_momentum_strategy(price_data, REBALANCING_FREQ, top_n=TOP_N)

# Get portfolio returns on benchmark strategy
bench_portfolio = (price_data[BENCHMARK]/price_data[BENCHMARK].iloc[0])*portfolio.iloc[0]

# Show metrics
print("Momentum strategy metrics:")
metrics = summary_metrics(portfolio)
print(metrics.to_string(index=False))

print("Benchmark portfolio metrics:")
bench_metrics = summary_metrics(bench_portfolio)
print(bench_metrics.to_string(index=False))

# Equity curve
plt.figure(figsize=(12, 6))
portfolio.plot(label="Momentum strategy", color="navy")
bench_portfolio.plot(label="Benchmark strategy", color="red")
plt.title("Equity Curve Top 3 ETF Momentum Strategy")
plt.xlabel("Date")
plt.ylabel("Portfolio value")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("equity_curve.png")
plt.show()