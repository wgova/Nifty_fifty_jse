import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf

def get_material_sens(symbol, months_back=6):
    """
    Get and analyze material SENS announcements for a stock.
    
    Args:
        symbol: Stock symbol (e.g., 'NPN.JO')
        months_back: Number of months to look back
        
    Returns:
        dict: Summary of material announcements
    """
    try:
        stock = yf.Ticker(symbol)
        
        # Get news and announcements
        news = stock.news
        
        if not news:
            return {
                'has_material_events': False,
                'summary': "No material SENS announcements found.",
                'events': []
            }
            
        # Filter for recent announcements
        cutoff_date = datetime.now() - timedelta(days=30 * months_back)
        recent_news = [
            item for item in news 
            if datetime.fromtimestamp(item['providerPublishTime']) > cutoff_date
        ]
        
        if not recent_news:
            return {
                'has_material_events': False,
                'summary': "No recent material SENS announcements found.",
                'events': []
            }
            
        # Categorize material events
        material_events = []
        for item in recent_news:
            title = item['title']
            date = datetime.fromtimestamp(item['providerPublishTime']).strftime('%Y-%m-%d')
            
            # Check for material keywords
            keywords = {
                'Financial Results': ['results', 'earnings', 'profit', 'loss', 'performance'],
                'Management Changes': ['ceo', 'cfo', 'executive', 'director', 'board', 'appoint', 'resign'],
                'Corporate Actions': ['acquisition', 'merger', 'disposal', 'restructure', 'rights issue'],
                'Dividends': ['dividend', 'distribution'],
                'Regulatory': ['investigation', 'fine', 'penalty', 'compliance'],
                'Strategic': ['strategy', 'expansion', 'contract', 'partnership']
            }
            
            for category, kwords in keywords.items():
                if any(kw in title.lower() for kw in kwords):
                    material_events.append({
                        'date': date,
                        'category': category,
                        'title': title
                    })
                    break
        
        # Create summary
        if material_events:
            summary = f"Found {len(material_events)} material announcements in the last {months_back} months."
            categories = set(event['category'] for event in material_events)
            category_summary = ", ".join(categories)
            summary += f"\nKey areas: {category_summary}"
        else:
            summary = "No material SENS announcements found in the specified period."
        
        return {
            'has_material_events': bool(material_events),
            'summary': summary,
            'events': sorted(material_events, key=lambda x: x['date'], reverse=True)
        }
        
    except Exception as e:
        return {
            'has_material_events': False,
            'summary': f"Error fetching SENS announcements: {str(e)}",
            'events': []
        }
