import yfinance as yf
import pandas as pd

# Extended JSE Top 50 stocks
JSE_TOP_50 = {
    'NPN.JO': 'Naspers',
    'PRX.JO': 'Prosus',
    'BTI.JO': 'British American Tobacco',
    'AGL.JO': 'Anglo American',
    'FSR.JO': 'FirstRand',
    'SBK.JO': 'Standard Bank',
    'MTN.JO': 'MTN Group',
    'VOD.JO': 'Vodacom',
    'GFI.JO': 'Gold Fields',
    'AMS.JO': 'Anglo American Platinum',
    'ABG.JO': 'Absa Group',
    'CPI.JO': 'Capitec Bank',
    'SOL.JO': 'Sasol',
    'SLM.JO': 'Sanlam',
    'REM.JO': 'Remgro',
    'ANG.JO': 'AngloGold Ashanti',
    'MCG.JO': 'MultiChoice Group',
    'BID.JO': 'Bid Corp',
    'NED.JO': 'Nedbank Group',
    'DSY.JO': 'Discovery'
}

def get_stock_data(symbol, period='5y'):
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        info = stock.info
        return hist, info
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
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
    except Exception as e:
        print(f"Error fetching metrics for {symbol}: {str(e)}")
        return {}

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