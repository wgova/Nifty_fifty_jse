import yfinance as yf
import pandas as pd
import os
from datetime import datetime
import base64
import requests
from io import BytesIO
import matplotlib.image as mpimg

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

        # Convert JSE stock prices from cents to rands
        if symbol.endswith('.JO'):
            for col in ['Open', 'High', 'Low', 'Close']:
                if col in hist.columns:
                    hist[col] = hist[col] / 100

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

        # Get additional info
        stock = yf.Ticker(symbol)
        info = stock.info

        # Convert financial metrics from cents to rands if needed
        if symbol.endswith('.JO'):
            for key in ['fiftyTwoWeekHigh', 'fiftyTwoWeekLow']:
                if key in info:
                    info[key] = info[key] / 100

        return hist, info
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None, None

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

        # Get dividend history
        dividends = stock.dividends
        latest_dividend = dividends.iloc[-1] if not dividends.empty else 0
        prev_dividend = dividends.iloc[-2] if len(dividends) > 1 else latest_dividend
        dividend_change = ((latest_dividend - prev_dividend) / prev_dividend * 100) if prev_dividend > 0 else 0
        latest_dividend_date = dividends.index[-1].strftime('%Y-%m-%d') if not dividends.empty else 'No dividends'

        # Convert JSE stock prices from cents to rands if needed
        if symbol.endswith('.JO'):
            latest_dividend = latest_dividend / 100 if latest_dividend else 0
            for key in ['fiftyTwoWeekHigh', 'fiftyTwoWeekLow']:
                if key in info:
                    info[key] = info[key] / 100

        metrics = {
            'Market Cap': info.get('marketCap', 'N/A'),
            'P/E Ratio': info.get('trailingPE', 'N/A'),
            'Forward P/E': info.get('forwardPE', 'N/A'),
            'PEG Ratio': info.get('pegRatio', 'N/A'),
            'Price/Book': info.get('priceToBook', 'N/A'),
            'Dividend Yield': info.get('dividendYield', 'N/A'),
            'Latest Dividend': latest_dividend,
            'Latest Dividend Date': latest_dividend_date,
            'Dividend Change': dividend_change,
            '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A'),
            'Beta': info.get('beta', 'N/A'),
            'Debt/Equity': info.get('debtToEquity', 'N/A'),
            'ROE': info.get('returnOnEquity', 'N/A'),
            'EPS': info.get('trailingEps', 'N/A'),
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

def get_company_logo(symbol: str) -> str:
    """Get company logo image as base64 string."""
    try:
        # Remove .JO suffix for lookup
        company_symbol = symbol.replace('.JO', '')

        # Example logo URLs (replace with actual JSE company logo URLs)
        logo_urls = {
            'NPN': 'https://www.naspers.com/logo.png',
            'PRX': 'https://www.prosus.com/logo.png',
            'MTN': 'https://www.mtn.com/logo.png',
            # Add more logo URLs as needed
        }

        if company_symbol in logo_urls:
            response = requests.get(logo_urls[company_symbol])
            if response.status_code == 200:
                return base64.b64encode(response.content).decode()

        # If no logo found or error, return empty string
        return ""
    except Exception as e:
        print(f"Error fetching logo for {symbol}: {str(e)}")
        return ""