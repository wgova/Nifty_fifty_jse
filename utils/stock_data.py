import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# Create data directory if it doesn't exist
DATA_DIR = "data/stock_data"
os.makedirs(DATA_DIR, exist_ok=True)

def download_and_save_stock_data(symbol, period='5y'):
    """Download stock data and save to CSV"""
    try:
        # Get stock data
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)

        if hist.empty:
            print(f"No data available for {symbol}")
            return None

        # Get date range for filename
        start_date = hist.index[0].strftime('%Y%m%d')
        end_date = hist.index[-1].strftime('%Y%m%d')

        # Create filename
        filename = f"{symbol}_{start_date}_{end_date}.csv"
        filepath = os.path.join(DATA_DIR, filename)

        # Save to CSV
        hist.to_csv(filepath)
        print(f"Saved data for {symbol} to {filepath}")

        return hist
    except Exception as e:
        print(f"Error downloading data for {symbol}: {str(e)}")
        return None

def get_stock_data(symbol, period='5y'):
    """Fetch stock data from Yahoo Finance and save locally"""
    try:
        # Download and save data
        hist = download_and_save_stock_data(symbol, period)
        
        # Check if we got valid data
        if hist is None or hist.empty:
            print(f"No data available for {symbol}")
            return None, {}

        # Get additional info with retry logic
        retries = 3
        info = {}
        
        for attempt in range(retries):
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                break
            except Exception as retry_error:
                print(f"Attempt {attempt+1}/{retries} failed for {symbol} info: {str(retry_error)}")
                if attempt == retries - 1:
                    print(f"All attempts failed for {symbol}")
                    info = {}

        return hist, info
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None, {}

# Extended JSE Top 50 stocks with sector information
JSE_TOP_50 = {
    # Technology & Media
    'NPN.JO': {'name': 'Naspers', 'sector': 'Technology'},
    'PRX.JO': {'name': 'Prosus', 'sector': 'Technology'},
    'MCG.JO': {'name': 'MultiChoice Group', 'sector': 'Technology'},

    # Telecommunications
    'MTN.JO': {'name': 'MTN Group', 'sector': 'Telecommunications'},
    'VOD.JO': {'name': 'Vodacom', 'sector': 'Telecommunications'},
    'TKG.JO': {'name': 'Telkom', 'sector': 'Telecommunications'},

    # Banking & Financial Services
    'FSR.JO': {'name': 'FirstRand', 'sector': 'Banking'},
    'SBK.JO': {'name': 'Standard Bank', 'sector': 'Banking'},
    'ABG.JO': {'name': 'Absa Group', 'sector': 'Banking'},
    'CPI.JO': {'name': 'Capitec Bank', 'sector': 'Banking'},
    'NED.JO': {'name': 'Nedbank Group', 'sector': 'Banking'},

    # Insurance
    'SLM.JO': {'name': 'Sanlam', 'sector': 'Insurance'},
    'DSY.JO': {'name': 'Discovery', 'sector': 'Insurance'},
    'OMU.JO': {'name': 'Old Mutual', 'sector': 'Insurance'},
    'MOM.JO': {'name': 'Momentum', 'sector': 'Insurance'},

    # Mining & Resources
    'AGL.JO': {'name': 'Anglo American', 'sector': 'Mining'},
    'GFI.JO': {'name': 'Gold Fields', 'sector': 'Mining'},
    'AMS.JO': {'name': 'Anglo American Platinum', 'sector': 'Mining'},
    'ANG.JO': {'name': 'AngloGold Ashanti', 'sector': 'Mining'},
    'IMP.JO': {'name': 'Impala Platinum', 'sector': 'Mining'}
}

def get_available_sectors():
    """Get list of unique sectors"""
    return sorted(list(set(stock['sector'] for stock in JSE_TOP_50.values())))

def get_stocks_by_sector(sector):
    """Get list of stocks in a specific sector"""
    return {symbol: data for symbol, data in JSE_TOP_50.items() if data['sector'] == sector}


def get_financial_metrics(symbol):
    """Get key financial metrics for a stock"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        metrics = {
            'Market Cap': info.get('marketCap', 'N/A'),
            'P/E Ratio': info.get('trailingPE', 'N/A'),
            'Dividend Yield': info.get('dividendYield', 'N/A'),
            '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A'),
        }
        return metrics
    except Exception as e:
        print(f"Error fetching metrics for {symbol}: {str(e)}")
        return {}

def calculate_sector_metrics(sector):
    """Calculate aggregate metrics for a sector"""
    sector_stocks = get_stocks_by_sector(sector)
    total_market_cap = 0
    weighted_pe = 0
    weighted_dividend_yield = 0
    total_weight = 0

    for symbol in sector_stocks:
        metrics = get_financial_metrics(symbol)
        market_cap = metrics.get('Market Cap', 0)
        if market_cap != 'N/A' and market_cap > 0:
            total_market_cap += market_cap
            weight = market_cap
            total_weight += weight

            pe_ratio = metrics.get('P/E Ratio', 0)
            if pe_ratio != 'N/A':
                weighted_pe += pe_ratio * weight

            div_yield = metrics.get('Dividend Yield', 0)
            if div_yield != 'N/A':
                weighted_dividend_yield += div_yield * weight

    if total_weight > 0:
        weighted_pe /= total_weight
        weighted_dividend_yield /= total_weight

    return {
        'Total Market Cap': total_market_cap,
        'Weighted P/E': weighted_pe,
        'Weighted Dividend Yield': weighted_dividend_yield,
        'Number of Companies': len(sector_stocks)
    }

def calculate_portfolio_metrics(selected_stocks, monthly_investment=100):
    """Calculate aggregate portfolio metrics"""
    total_market_cap = 0
    weighted_pe = 0
    weighted_dividend_yield = 0
    total_weight = 0

    for symbol in selected_stocks:
        metrics = get_financial_metrics(symbol)
        market_cap = metrics.get('Market Cap', 0)
        if market_cap != 'N/A' and market_cap > 0:
            total_market_cap += market_cap
            weight = market_cap
            total_weight += weight

            pe_ratio = metrics.get('P/E Ratio', 0)
            if pe_ratio != 'N/A':
                weighted_pe += pe_ratio * weight

            div_yield = metrics.get('Dividend Yield', 0)
            if div_yield != 'N/A':
                weighted_dividend_yield += div_yield * weight

    if total_weight > 0:
        weighted_pe /= total_weight
        weighted_dividend_yield /= total_weight

    return {
        'Total Market Cap': total_market_cap,
        'Weighted P/E': weighted_pe,
        'Weighted Dividend Yield': weighted_dividend_yield
    }