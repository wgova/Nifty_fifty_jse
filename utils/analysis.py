import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple

def calculate_portfolio_value(stock_data: pd.DataFrame, monthly_investment: float = 100) -> pd.Series:
    """
    Calculate portfolio value with monthly investments.

    Args:
        stock_data: DataFrame with stock price history
        monthly_investment: Monthly investment amount in Rands

    Returns:
        Series with portfolio values over time
    """
    if stock_data is None or stock_data.empty:
        return pd.Series()

    try:
        # Ensure data is properly formatted
        stock_data = stock_data.copy()
        stock_data.index = pd.to_datetime(stock_data.index)
        stock_data['Close'] = pd.to_numeric(stock_data['Close'], errors='coerce')

        # Remove any NaN values
        stock_data = stock_data.dropna(subset=['Close'])

        # Resample to month-end and calculate portfolio value
        monthly_data = stock_data.resample('ME').last()
        portfolio_value = []
        investment_amount = 0
        shares = 0

        for price in monthly_data['Close']:
            investment_amount += monthly_investment
            if not pd.isna(price) and price > 0:
                new_shares = monthly_investment / price
                shares += new_shares
                current_value = shares * price
                portfolio_value.append(current_value)
            else:
                portfolio_value.append(portfolio_value[-1] if portfolio_value else investment_amount)

        return pd.Series(portfolio_value, index=monthly_data.index)
    except Exception as e:
        print(f"Error calculating portfolio value: {str(e)}")
        return pd.Series()

def calculate_returns(portfolio_values: pd.Series) -> Tuple[float, float, float]:
    """
    Calculate portfolio returns and annualized metrics.

    Args:
        portfolio_values: Series of portfolio values over time

    Returns:
        Tuple of (total_return_pct, annualized_return_pct, volatility)
    """
    if portfolio_values is None or len(portfolio_values) < 2:
        return 0.0, 0.0, 0.0

    try:
        # Calculate returns
        initial_value = portfolio_values.iloc[0]
        final_value = portfolio_values.iloc[-1]
        if initial_value == 0:
            return 0.0, 0.0, 0.0

        # Total return
        total_return = ((final_value - initial_value) / initial_value) * 100

        # Calculate time period in years
        years = (portfolio_values.index[-1] - portfolio_values.index[0]).days / 365.25

        # Annualized return
        annualized_return = ((1 + total_return/100) ** (1/years) - 1) * 100 if years > 0 else 0

        # Calculate volatility
        returns = portfolio_values.pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100  # Annualized volatility

        return total_return, annualized_return, volatility
    except Exception as e:
        print(f"Error calculating returns: {str(e)}")
        return 0.0, 0.0, 0.0

def get_summary_statistics(stock_data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate comprehensive summary statistics for a stock.

    Args:
        stock_data: DataFrame with stock price history

    Returns:
        Dictionary containing summary statistics
    """
    if stock_data is None or stock_data.empty:
        return {
            'Mean': 0.0,
            'Std Dev': 0.0,
            'Min': 0.0,
            'Max': 0.0,
            'Median': 0.0,
            'Daily Return': 0.0,
            'Volatility': 0.0
        }

    try:
        # Calculate basic statistics
        stats = {
            'Mean': stock_data['Close'].mean(),
            'Std Dev': stock_data['Close'].std(),
            'Min': stock_data['Close'].min(),
            'Max': stock_data['Close'].max(),
            'Median': stock_data['Close'].median(),
        }

        # Calculate daily returns and volatility
        returns = stock_data['Close'].pct_change().dropna()
        stats['Daily Return'] = returns.mean() * 100  # as percentage
        stats['Volatility'] = returns.std() * np.sqrt(252) * 100  # annualized

        return stats
    except Exception as e:
        print(f"Error calculating summary statistics: {str(e)}")
        return {
            'Mean': 0.0,
            'Std Dev': 0.0,
            'Min': 0.0,
            'Max': 0.0,
            'Median': 0.0,
            'Daily Return': 0.0,
            'Volatility': 0.0
        }

def prepare_chart_data(stock_data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Prepare data for charting with proper validation and formatting.

    Args:
        stock_data: DataFrame with stock price history

    Returns:
        Tuple of (processed_data, chart_metrics)
    """
    if stock_data is None or stock_data.empty:
        return pd.DataFrame(), {}

    try:
        # Create a copy to avoid modifying original data
        df = stock_data.copy()

        # Ensure datetime index
        df.index = pd.to_datetime(df.index)

        # Convert price columns to numeric
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Convert volume to numeric
        if 'Volume' in df.columns:
            df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')

        # Remove any NaN values
        df = df.dropna(subset=['Close'])

        # Calculate additional metrics for charting
        metrics = {
            'latest_price': df['Close'].iloc[-1] if not df.empty else 0.0,
            'price_change': df['Close'].pct_change().iloc[-1] * 100 if not df.empty else 0.0,
            'volume_avg': df['Volume'].mean() if 'Volume' in df.columns else 0.0,
            'price_max': df['High'].max() if 'High' in df.columns else df['Close'].max(),
            'price_min': df['Low'].min() if 'Low' in df.columns else df['Close'].min()
        }

        return df, metrics
    except Exception as e:
        print(f"Error preparing chart data: {str(e)}")
        return pd.DataFrame(), {}