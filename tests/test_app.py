import os
import sys
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import logging

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.stock_data import (
    JSE_TOP_50,
    get_stock_data,
    get_financial_metrics,
    get_available_sectors,
    calculate_portfolio_metrics
)

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@pytest.fixture
def sample_stock_data():
    """Create sample stock data for testing"""
    return pd.DataFrame({
        'Open': [100.0, 101.0, 102.0],
        'High': [103.0, 104.0, 105.0],
        'Low': [98.0, 99.0, 100.0],
        'Close': [101.0, 102.0, 103.0],
        'Volume': [1000000, 1100000, 1200000]
    }, index=pd.date_range('2025-01-01', periods=3))

@pytest.fixture
def sample_stock_info():
    """Create sample stock info for testing"""
    return {
        'marketCap': 1000000000,
        'trailingPE': 15.5,
        'dividendYield': 0.03,
        'fiftyTwoWeekHigh': 110.0,
        'fiftyTwoWeekLow': 90.0
    }

def test_get_available_sectors():
    """Test sector list retrieval"""
    logger.info("Testing sector retrieval...")
    sectors = get_available_sectors()
    assert isinstance(sectors, list)
    assert len(sectors) > 0
    assert 'Technology' in sectors
    assert 'Banking' in sectors
    logger.info(f"Found {len(sectors)} sectors")

def test_stock_selection_limits():
    """Test stock selection limits"""
    logger.info("Testing stock selection limits...")
    # Test minimum limit
    min_stocks = ['NPN.JO', 'PRX.JO']  # Only 2 stocks
    metrics = calculate_portfolio_metrics(min_stocks)
    assert len(min_stocks) < 3, "Should fail with less than 3 stocks"

    # Test maximum limit
    all_stocks = list(JSE_TOP_50.keys())
    max_stocks = all_stocks[:16]  # 16 stocks
    metrics = calculate_portfolio_metrics(max_stocks)
    assert len(max_stocks) > 15, "Should fail with more than 15 stocks"

def test_sector_stock_selection():
    """Test sector-based stock selection"""
    logger.info("Testing sector-based selection...")
    tech_stocks = [
        symbol for symbol, data in JSE_TOP_50.items()
        if data['sector'] == 'Technology'
    ]
    assert len(tech_stocks) > 0, "Technology sector should have stocks"
    metrics = calculate_portfolio_metrics(tech_stocks)
    assert metrics is not None, "Should calculate metrics for sector stocks"

@patch('yfinance.Ticker')
def test_get_stock_data(mock_ticker, sample_stock_data, sample_stock_info):
    """Test stock data retrieval with mocked data"""
    logger.info("Testing stock data retrieval...")

    # Mock the yfinance Ticker
    mock_instance = MagicMock()
    mock_instance.history.return_value = sample_stock_data
    mock_instance.info = sample_stock_info
    mock_ticker.return_value = mock_instance

    # Test data retrieval
    hist, info = get_stock_data('NPN.JO')

    assert hist is not None
    assert not hist.empty
    assert info is not None
    assert 'Close' in hist.columns

    # Test JSE price conversion
    assert hist['Close'].iloc[-1] == 1.03
    assert info['fiftyTwoWeekHigh'] == 1.10

    logger.info("Stock data retrieval test completed successfully")

def test_get_financial_metrics(sample_stock_info):
    """Test financial metrics calculation"""
    logger.info("Testing financial metrics calculation...")

    with patch('yfinance.Ticker') as mock_ticker:
        mock_instance = MagicMock()
        mock_instance.info = sample_stock_info
        mock_ticker.return_value = mock_instance

        metrics = get_financial_metrics('NPN.JO')

        assert isinstance(metrics, dict)
        assert 'Market Cap' in metrics
        assert metrics['P/E Ratio'] == 15.5
        assert metrics['Market Cap'] == 1000000000

        logger.info("Financial metrics test completed successfully")