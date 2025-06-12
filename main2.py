# main.py
import pandas as pd
from data_downloader import download_data
#from backtest import run_momentum_strategy
from backtest2 import MomentumBacktester
from metrics import summary_metrics
import matplotlib.pyplot as plt

# Parameters
TICKERS = ["SPY", "QQQ", "IWM", "EEM", "EFA", "XLF", "HYG", "TLT", "XLE", "LQD", "XLV", "DIA", "GLD", "XLU", "JNK", "SOXL", "XLK", 
           "XBI", "ARKK", "UVXY", "FXI", "VEA", "EWZ", "VXX", "SH", "PSQ", "TQQQ", "SQQQ", "VOO", "IVV"]
START_DATE = "2010-01-01"
END_DATE = "2024-12-31"
TOP_N = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
BENCHMARK = 'SPY'
REBALANCING_FREQ = ['1D', '1W', '2W', '1ME', '2ME', '1Q', '2Q']
REDOWNLOAD_DATA = False # If we want to have fresh data downloaded or work on previously downloaded

if REDOWNLOAD_DATA:
    # Data download
    print("Downloading data...")
    price_data = download_data(TICKERS, start=START_DATE, end=END_DATE)
    price_data.to_csv("etf_data.csv")
else:
    print("Data loaded from local drive...")
    # Data loading
    price_data = pd.read_csv("etf_data.csv", index_col="Date", date_format="%Y-%m-%d")

# Run the strategy for different values of rebalancing frequency and top N
for rebalancing_freq in REBALANCING_FREQ:
    for top_n in TOP_N:
        print(f"Running the momentum strategy, rebalancing freq: {rebalancing_freq}, top {top_n} ETFs...")
        # Instantiate backtester
        bt = MomentumBacktester(price_data, rebalancing_freq, top_n, lookback_3m=3, lookback_12m=12)
        # Run backtest
        portfolio, weights = bt.run()
        # Get portfolio returns on benchmark strategy
        price_benchmark = price_data[BENCHMARK].resample(rebalancing_freq).last()
        bench_portfolio = (price_benchmark/price_benchmark.iloc[0])*portfolio.iloc[0]
        # Show metrics
        print(f"Momentum strategy metrics, rebalancing freq: {rebalancing_freq}, top {top_n} ETFs...")
        metrics = summary_metrics(portfolio)
        print(metrics.to_string(index=False))
        print(f"Benchmark portfolio metrics, rebalancing freq: {rebalancing_freq}, top {top_n} ETFs...")
        bench_metrics = summary_metrics(bench_portfolio)
        print(bench_metrics.to_string(index=False))
        # Equity curve
        plt.figure(figsize=(12, 6))
        portfolio.plot(label="Momentum strategy", color="navy")
        bench_portfolio.plot(label="Benchmark strategy", color="red")
        plt.title(f"Equity Curve Top 3 ETF Momentum Strategy, rebalancing freq: {rebalancing_freq}, top {top_n} ETFs...")
        plt.xlabel("Date")
        plt.ylabel("Portfolio value")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"equity_curve_{rebalancing_freq}_top_{top_n}_etfs.png")
        plt.show()