import pandas as pd
import numpy as np

def calculate_portfolio_value(stock_data, monthly_investment=100):
    """Calculate portfolio value with monthly investments"""
    if stock_data.empty:
        return None
    
    monthly_data = stock_data.resample('M').last()
    portfolio_value = []
    investment_amount = 0
    
    for price in monthly_data['Close']:
        investment_amount += monthly_investment
        shares = monthly_investment / price
        portfolio_value.append(investment_amount)
    
    return pd.Series(portfolio_value, index=monthly_data.index)

def calculate_returns(portfolio_values):
    """Calculate portfolio returns"""
    if portfolio_values is None:
        return None
    
    initial_value = portfolio_values.iloc[0]
    final_value = portfolio_values.iloc[-1]
    total_return = ((final_value - initial_value) / initial_value) * 100
    return total_return

def get_summary_statistics(stock_data):
    """Calculate summary statistics for a stock"""
    return {
        'Mean': stock_data['Close'].mean(),
        'Std Dev': stock_data['Close'].std(),
        'Min': stock_data['Close'].min(),
        'Max': stock_data['Close'].max(),
    }
