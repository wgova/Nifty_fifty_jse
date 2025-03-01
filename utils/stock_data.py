import yfinance as yf
import pandas as pd

# JSE Top 50 stocks (sample list - you can expand this)
JSE_TOP_50 = {
    'NPN.JO': 'Naspers',
    'PRX.JO': 'Prosus',
    'BTI.JO': 'British American Tobacco',
    'AGL.JO': 'Anglo American',
    'FSR.JO': 'FirstRand',
    'SBK.JO': 'Standard Bank',
}

def get_stock_data(symbol, period='5y'):
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        info = stock.info
        return hist, info
    except Exception as e:
        return None, None

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
    except:
        return {}
