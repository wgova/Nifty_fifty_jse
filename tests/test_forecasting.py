import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.forecasting import create_forecast, calculate_forecast_returns

@pytest.fixture
def sample_stock_data():
    """Create sample stock data for testing forecasts"""
    dates = pd.date_range(start='2025-01-01', periods=100, freq='D')
    data = pd.DataFrame({
        'Close': np.linspace(100, 200, 100) + np.random.normal(0, 5, 100),
        'Open': np.linspace(98, 198, 100) + np.random.normal(0, 5, 100),
        'High': np.linspace(102, 202, 100) + np.random.normal(0, 5, 100),
        'Low': np.linspace(97, 197, 100) + np.random.normal(0, 5, 100),
        'Volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    return data

def test_create_forecast(sample_stock_data):
    """Test forecast creation with confidence intervals"""
    # Test basic forecast creation
    median, lower, upper = create_forecast(sample_stock_data, months_ahead=6)
    
    assert not median.empty, "Median forecast should not be empty"
    assert not lower.empty, "Lower bound should not be empty"
    assert not upper.empty, "Upper bound should not be empty"
    assert len(median) == len(lower) == len(upper), "All forecasts should have same length"
    assert all(lower <= median), "Lower bound should be <= median"
    assert all(median <= upper), "Median should be <= upper bound"

def test_forecast_with_empty_data():
    """Test forecast handling of empty data"""
    empty_df = pd.DataFrame()
    median, lower, upper = create_forecast(empty_df, months_ahead=6)
    
    assert isinstance(median, pd.Series), "Should return empty Series for empty input"
    assert median.empty, "Should return empty forecast for empty input"

def test_calculate_forecast_returns():
    """Test return calculations with monthly investments"""
    # Create simple increasing forecast
    dates = pd.date_range(start='2025-01-01', periods=6, freq='M')
    forecast = pd.Series([100, 110, 120, 130, 140, 150], index=dates)
    
    investment, returns, percentage = calculate_forecast_returns(forecast, monthly_investment=1000)
    
    assert investment > 0, "Investment amount should be positive"
    assert returns > 0, "Returns should be positive for increasing forecast"
    assert percentage > 0, "Return percentage should be positive"

def test_extreme_values():
    """Test handling of extreme values"""
    # Create forecast with extreme values
    dates = pd.date_range(start='2025-01-01', periods=6, freq='M')
    extreme_forecast = pd.Series([100, 1000, 10000, 100000, 1000000, 10000000], index=dates)
    
    investment, returns, percentage = calculate_forecast_returns(extreme_forecast, monthly_investment=1000)
    
    assert not np.isinf(returns), "Returns should not be infinite"
    assert not np.isinf(percentage), "Percentage should not be infinite"
    assert not np.isnan(returns), "Returns should not be NaN"
    assert not np.isnan(percentage), "Percentage should not be NaN"

def test_negative_values():
    """Test handling of negative values"""
    dates = pd.date_range(start='2025-01-01', periods=6, freq='M')
    negative_forecast = pd.Series([100, 90, 80, 70, 60, 50], index=dates)
    
    investment, returns, percentage = calculate_forecast_returns(negative_forecast, monthly_investment=1000)
    
    assert investment > 0, "Investment should be positive"
    assert returns < 0, "Returns should be negative for decreasing forecast"
    assert percentage < 0, "Percentage should be negative for loss"
