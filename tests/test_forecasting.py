import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.forecasting import create_forecast, calculate_forecast_returns

@pytest.fixture
def sample_stock_data():
    """Create sample stock data for testing forecasting"""
    dates = pd.date_range(start='2024-01-01', end='2025-01-01', freq='D')
    data = pd.DataFrame({
        'Close': np.linspace(100, 150, len(dates)) + np.random.normal(0, 5, len(dates)),
        'Volume': np.random.randint(1000, 10000, len(dates))
    }, index=dates)
    return data

def test_create_forecast(sample_stock_data):
    """Test forecast creation with confidence intervals"""
    # Create forecast
    median_forecast, lower_bound, upper_bound = create_forecast(sample_stock_data, months_ahead=3)
    
    # Check basic properties
    assert len(median_forecast) == 90  # 3 months * 30 days
    assert len(lower_bound) == len(median_forecast)
    assert len(upper_bound) == len(median_forecast)
    
    # Check confidence interval relationships
    assert all(lower_bound <= median_forecast)
    assert all(median_forecast <= upper_bound)
    
    # Check forecast continuation
    assert abs(median_forecast.iloc[0] - sample_stock_data['Close'].iloc[-1]) < 20

def test_calculate_forecast_returns(sample_stock_data):
    """Test forecast returns calculation"""
    median_forecast, _, _ = create_forecast(sample_stock_data, months_ahead=3)
    
    # Test with different monthly investments
    monthly_investment = 1000
    total_investment, total_return, return_percentage = calculate_forecast_returns(
        median_forecast, monthly_investment
    )
    
    # Basic validation
    assert total_investment > 0
    assert isinstance(total_return, float)
    assert isinstance(return_percentage, float)
    assert total_investment == monthly_investment * 3  # 3 months

def test_empty_data_handling():
    """Test handling of empty or invalid data"""
    empty_df = pd.DataFrame()
    
    # Test forecast creation with empty data
    median_forecast, lower_bound, upper_bound = create_forecast(empty_df)
    assert len(median_forecast) == 0
    assert len(lower_bound) == 0
    assert len(upper_bound) == 0
    
    # Test returns calculation with empty forecast
    total_investment, total_return, return_percentage = calculate_forecast_returns(
        pd.Series(), monthly_investment=100
    )
    assert total_investment == 0
    assert total_return == 0
    assert return_percentage == 0
