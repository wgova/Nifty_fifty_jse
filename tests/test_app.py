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
    get_available_sectors
)

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
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

@patch('yfinance.Ticker')
def test_get_stock_data(mock_ticker, sample_stock_data, sample_stock_info):
    """Test stock data retrieval"""
    logger.info("Testing stock data retrieval...")

    # Mock the yfinance Ticker
    mock_instance = MagicMock()
    mock_instance.history.return_value = sample_stock_data
    mock_instance.info = sample_stock_info
    mock_ticker.return_value = mock_instance

    # Test data retrieval
    hist, info = get_stock_data('NPN.JO')

    # Test basic data integrity
    assert hist is not None
    assert not hist.empty
    assert info is not None
    assert 'Close' in hist.columns

    # Test price conversion (JSE prices are converted from cents to rands)
    # Expected: 103.0 cents = 1.03 rands
    assert hist['Close'].iloc[-1] == 1.03
    assert hist['Open'].iloc[0] == 1.00
    assert hist['High'].iloc[-1] == 1.05
    assert hist['Low'].iloc[0] == 0.98

    # Test info data
    assert info['marketCap'] == 1000000000
    assert info['trailingPE'] == 15.5
    assert info['fiftyTwoWeekHigh'] == 1.10  # 110.0/100
    assert info['fiftyTwoWeekLow'] == 0.90   # 90.0/100

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
        assert 'P/E Ratio' in metrics
        assert metrics['P/E Ratio'] == 15.5
        assert metrics['Market Cap'] == 1000000000

        logger.info("Financial metrics test completed successfully")

def test_jse_top_50_structure():
    """Test JSE Top 50 dictionary structure"""
    logger.info("Testing JSE Top 50 structure...")

    assert isinstance(JSE_TOP_50, dict)
    assert len(JSE_TOP_50) > 0

    # Test a specific stock entry
    naspers = JSE_TOP_50.get('NPN.JO')
    assert naspers is not None
    assert naspers['name'] == 'Naspers'
    assert naspers['sector'] == 'Technology'

    logger.info("JSE Top 50 structure test completed successfully")