# backtest.py
import pandas as pd
import numpy as np

def process(in_data):
    """
    Parameters:
        input_data (pd.DataFrame): Raw dataframe.
    Returns:
        out_data (pd.DataFrame): A dataframe ready to be used by run_momentum_strategy().
    """
    # Convert date column to datetime
    in_data['Date'] = pd.to_datetime(in_data['Date'], format='%Y-%m-%d')
    # Set 'Date' as index
    out_data = in_data.set_index('Date')
    return out_data


def run_momentum_strategy(price_data, top_n=3):
    """
    Momentum strategy. Select top_n ETFs based on the highest 3M returns.
    Parameters:
        price_data (pd.DataFrame): ETFs' close prices.
        top_n (int): How many ETFs to select? Default: 3.
    Returns:
        portfolio (pd.DataFrame): Portfolio value.
    """
    # Process the input data
    price_data = process(price_data)
    # Calculate returns
    #returns = price_data.pct_change()
    # Convert to monthly prices and returns
    monthly_prices = price_data.resample("ME").last()
    monthly_returns = monthly_prices.pct_change()
    # A series to store monthly portfolio values
    portfolio = pd.Series(index=monthly_prices.index, dtype=float)
    # A dataframe to store ETFs weights
    weights_history = pd.DataFrame(index=monthly_prices.index, columns=price_data.columns)
    # Start looping from the 12th month (1 year)
    for i in range(12, len(monthly_prices)-1):
        date = monthly_prices.index[i]
        next_month_date = monthly_prices.index[i+1]
        # Lookback periods
        past_3m = monthly_prices.iloc[i-3:i]
        past_12m = monthly_prices.iloc[i-12:i]
        # 3M and 12M returns
        perf_3m = past_3m.iloc[-1]/past_3m.iloc[0] - 1
        perf_12m = past_12m.iloc[-1]/past_12m.iloc[0] - 1
        # Filter in positive returns only
        eligible = perf_12m[perf_12m > 0].index
        selected = perf_3m[eligible].sort_values(ascending=False).head(top_n).index
        # Assign weights
        weights = pd.Series(0.0, index=price_data.columns)
        weights[selected] = 1/top_n  # Equal weight
        weights_history.loc[date] = weights
        # Portfolio return in a month
        next_month_return = monthly_returns.iloc[i+1]
        portfolio[next_month_date] = (weights*next_month_return).sum()
    # Portfolio value in time   
    portfolio = (1 + portfolio.fillna(0)).cumprod()
    return portfolio, weights_history

