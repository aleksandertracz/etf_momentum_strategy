# metrics.py
import pandas as pd
import numpy as np

def calculate_cagr(portfolio):
    """
    CAGR - compound annual growth rate.
    Parameters:
        portfolio (pd.Series): Portfolio returns.
    Returns:
        cagr (float): CAGR value.
    """
    n_years = (portfolio.index[-1] - portfolio.index[0]).days / 365.25
    cagr = (portfolio.iloc[-1] / portfolio.iloc[0])**(1 / n_years) - 1
    return cagr

def calculate_volatility(portfolio):
    """
    Annualized volatility of daily log-returns.
    Parameters:
        portfolio (pd.Series): Portfolio returns.
    Returns:
        vol (float): Portfolio returns volatility.
    """
    logreturns = np.log(portfolio / portfolio.shift(1))
    vol = logreturns.std() * np.sqrt(252)
    return vol

def calculate_sharpe_ratio(portfolio, rfr = 0.02):
    """
    Sharpe ratio: (CAGR - rf) / Volatility.
    Parameters:
        portfolio (pd.Series): Portfolio returns.
        rfr (float): Risk-free rate. Default: 0.02.
    Returns:
        sr (float): Portfolio's Sharpe ratio.
    """
    cagr = calculate_cagr(portfolio)
    vol = calculate_volatility(portfolio)
    if vol == 0:
        return np.nan
    sr = (cagr - rfr) / vol
    return sr

def calculate_max_drawdown(portfolio):
    """
    Max drawdown across the whole sample.
    Parameters:
        portfolio (pd.Series): Portfolio returns.
    Returns:
        max_drawdown (float): Portfolio's maximum drawdown.
    """
    rolling_max = portfolio.cummax()
    drawdown = portfolio / rolling_max - 1
    max_drawdown = drawdown.min()
    return max_drawdown

def summary_metrics(portfolio):
    """
    A dataframe of metrics. Uses calculate_cagr(), calculate_volatility(), calculate_sharpe_ratio() and 
    calculate_max_drawdown().
    Parameters:
        portfolio (pd.Series): Portfolio returns.
    Returns:
        metrics (pd.DataFrame): Portfolio's metrics.
    """
    metrics = pd.DataFrame({
        "CAGR": [calculate_cagr(portfolio)],
        "Ann. Volatility": [calculate_volatility(portfolio)],
        "Sharpe Ratio": [calculate_sharpe_ratio(portfolio)],
        "Max Drawdown": [calculate_max_drawdown(portfolio)]
    })
    return metrics