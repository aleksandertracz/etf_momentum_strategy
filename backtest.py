# backtest.py
import pandas as pd

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

def run_momentum_strategy(price_data, rebalancing_freq, top_n=3):
    """
    Momentum strategy. Select top_n ETFs based on the highest 3M returns.
    Parameters:
        price_data (pd.DataFrame): ETFs' close prices.
        rebalancing_freq (string): Frequency with which to rebalance the portfolio.
        top_n (int): How many ETFs to select? Default: 3.
    Returns:
        portfolio (pd.DataFrame): Portfolio value.
    """
    # Process the input data
    #price_data = process(price_data)
    # Calculate returns
    #returns = price_data.pct_change()
    # Convert to monthly prices and returns
    rebal_prices = price_data.resample(rebalancing_freq).last().fillna("ffill")
    rebal_returns = rebal_prices.pct_change()
    # A series to store monthly portfolio values
    portfolio = pd.Series(index=rebal_prices.index, dtype=float)
    # A dataframe to store ETFs weights
    weights_history = pd.DataFrame(index=rebal_prices.index, columns=price_data.columns)
    # Start looping from after the 1st year of the sample
    min_lookback = pd.DateOffset(months=12)
    first_valid_date = rebal_prices.index[0] + min_lookback
    valid_dates = rebal_prices.index[rebal_prices.index >= first_valid_date]
    for date in valid_dates:
        # Get position of the date in valid_dates
        i = valid_dates.get_loc(date)
        #date = monthly_prices.index[i]
        #next_month_date = monthly_prices.index[i+1]
        # Lookback periods
        lookbacks = {'3m': date-pd.DateOffset(months=3), '12m': date-pd.DateOffset(months=12)}
        # Find the closest available historical prices (using .asof for backward fill)
        past_3m = rebal_prices.loc[lookbacks['3m']:date]
        past_12m = rebal_prices.loc[lookbacks['12m']:date]
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
        # Portfolio return in the end of next period
        if i+1 < len(valid_dates):
            next_period = valid_dates[i+1]
        next_period_return = rebal_returns.loc[next_period]
        portfolio[next_period] = (weights*next_period_return).sum()
    # Portfolio value in time   
    portfolio = (1 + portfolio.fillna(0)).cumprod()
    return portfolio, weights_history