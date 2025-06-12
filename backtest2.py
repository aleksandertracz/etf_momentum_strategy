import pandas as pd
import numpy as np
import logging

# Setup logging for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Backtester class
class MomentumBacktester:
    def __init__(self, price_data, rebalancing_freq, top_n, lookback_3m=3, lookback_12m=12):
        """
        Initialize the momentum backtester.
        Parameters:
            price_data (pd.DataFrame): Historical ETF price data with DateTimeIndex.
            rebalancing_freq (str): Portfolio rebalancing frequency (e.g., '1ME', 'W'). Must be accepted by pd.DataFrame.resample() function.
            top_n (int): A number of ETFs to select.
            lookback_3m (int): Lookback period in months for short-term momentum.
            lookback_12m (int): Lookback period in months for long-term filter.
        """
        self.price_data = price_data.sort_index()
        self.rebalancing_freq = rebalancing_freq
        self.top_n = top_n
        self.lookback_3m = lookback_3m
        self.lookback_12m = lookback_12m

        # Validate data
        self._validate_data()

    def _validate_data(self):
        if not isinstance(self.price_data.index, pd.DatetimeIndex):
            raise ValueError("Price data must have a DatetimeIndex.")
        if self.price_data.isnull().any().any():
            logging.warning("Price data contains NaNs. Consider cleaning or forward filling.")
    
    def run(self):
        """
        Run the momentum backtest.
        Returns:
            portfolio_value (pd.Series): Portfolio cumulative return.
            weights_history (pd.DataFrame): Historical portfolio weights.
        """
        # Resample prices
        rebal_prices = self.price_data.resample(self.rebalancing_freq).last()
        # Compute periodic returns for portfolio return calculation
        rebal_returns = rebal_prices.pct_change()
        # Series to store portfolio values and weights
        portfolio = pd.Series(index=rebal_prices.index, dtype=float)
        weights_history = pd.DataFrame(index=rebal_prices.index, columns=self.price_data.columns)
        # Start looping from after the 1st lookback period of the sample
        first_valid_date = rebal_prices.index[0] + pd.DateOffset(months=self.lookback_12m)
        valid_dates = rebal_prices.index[rebal_prices.index >= first_valid_date]
        for i, date in enumerate(valid_dates):
            # Lookback windows
            past_3m_start = date - pd.DateOffset(months=self.lookback_3m)
            past_12m_start = date - pd.DateOffset(months=self.lookback_12m)
            try:
                past_3m = rebal_prices.loc[past_3m_start:date]
                past_12m = rebal_prices.loc[past_12m_start:date]
                # Lookback periods performance
                perf_3m = past_3m.iloc[-1] / past_3m.iloc[0] - 1
                perf_12m = past_12m.iloc[-1] / past_12m.iloc[0] - 1
                # Filter ETFs
                eligible_assets = perf_12m[perf_12m > 0].index
                selected_assets = perf_3m[eligible_assets].sort_values(ascending=False).head(self.top_n).index
                # Assign weights
                weights = pd.Series(0.0, index=self.price_data.columns)
                weights[selected_assets] = 1 / self.top_n
                weights_history.loc[date] = weights
                # Compute portfolio return in next period
                if i+1 < len(valid_dates):
                    next_date = valid_dates[i+1]
                    next_return = rebal_returns.loc[next_date].fillna(0)
                    portfolio[next_date] = (weights * next_return).sum()
            except Exception as e:
                logging.error(f"Error processing date {date}: {e}")
                continue
        # Compute cumulative portfolio value
        portfolio = (1 + portfolio.fillna(0)).cumprod()
        portfolio.iloc[0] = 1.0  # start at 1
        return portfolio, weights_history