import pandas as pd
import numpy as np

def calculate_portfolio_value(stock_data, monthly_investment=100):
    """Calculate portfolio value with monthly investments"""
    if stock_data is None or stock_data.empty:
        return pd.Series()

    # Use 'ME' instead of 'M' for month end frequency
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

def calculate_returns(portfolio_values):
    """Calculate portfolio returns"""
    if portfolio_values is None or len(portfolio_values) == 0:
        return 0.0

    initial_value = portfolio_values.iloc[0]
    final_value = portfolio_values.iloc[-1]
    if initial_value == 0:
        return 0.0

    total_return = ((final_value - initial_value) / initial_value) * 100
    return total_return

def get_summary_statistics(stock_data):
    """Calculate summary statistics for a stock"""
    if stock_data is None or stock_data.empty:
        return {
            'Mean': 0.0,
            'Std Dev': 0.0,
            'Min': 0.0,
            'Max': 0.0,
        }

    return {
        'Mean': stock_data['Close'].mean(),
        'Std Dev': stock_data['Close'].std(),
        'Min': stock_data['Close'].min(),
        'Max': stock_data['Close'].max(),
    }