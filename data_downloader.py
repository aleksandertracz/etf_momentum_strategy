# data_downloader.py
import yfinance as yf
import pandas as pd

def download_data(tickers, start="2010-01-01", end="2024-12-31"):
    data = yf.download(tickers, start=start, end=end, progress=False)["Close"]
    return data.dropna(how="all")

if __name__ == "__main__":
    # I'm looking at ETFs with daily volume over 0.5 bln USD (2025-06-05)
    tickers = [
        "SPY", "QQQ", "IWM", "EEM", "EFA", "XLF", "HYG", "TLT", "XLE", "LQD",
        "XLV", "DIA", "GLD", "XLU", "JNK", "SOXL", "XLK", "XBI", "ARKK", "UVXY",
        "FXI", "VEA", "EWZ", "VXX", "SH", "PSQ", "TQQQ", "SQQQ", "VOO", "IVV"
    ]
    df = download_data(tickers)
    df.to_csv("etf_data.csv")