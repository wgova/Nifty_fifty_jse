import pandas as pd
from datetime import datetime, timedelta
import trafilatura
import re
from typing import Dict, List

def get_material_sens(symbol: str, months_back: int = 6) -> Dict:
    """
    Get and analyze material SENS announcements for a stock using web scraping.

    Args:
        symbol: Stock symbol (e.g., 'NPN.JO')
        months_back: Number of months to look back

    Returns:
        dict: Summary of material announcements
    """
    try:
        # Remove .JO suffix for JSE lookup
        company_symbol = symbol.replace('.JO', '')

        # Example JSE SENS URL (modify as needed)
        url = f"https://www.jse.co.za/cx/company-announcements/{company_symbol}"

        # Get webpage content
        downloaded = trafilatura.fetch_url(url)
        text_content = trafilatura.extract(downloaded)

        if not text_content:
            return {
                'has_material_events': False,
                'summary': "No SENS announcements could be retrieved.",
                'events': []
            }

        # Parse announcements using regex patterns
        announcements = parse_sens_content(text_content)

        # Filter for recent announcements
        cutoff_date = datetime.now() - timedelta(days=30 * months_back)
        recent_announcements = []

        for announcement in announcements:
            try:
                announcement_date = datetime.strptime(announcement['date'], '%Y-%m-%d')
                if announcement_date > cutoff_date:
                    recent_announcements.append(announcement)
            except ValueError:
                continue

        if not recent_announcements:
            return {
                'has_material_events': False,
                'summary': f"No material SENS announcements found in the last {months_back} months.",
                'events': []
            }

        # Categorize announcements
        categorized_events = categorize_announcements(recent_announcements)

        # Create summary
        summary = f"Found {len(categorized_events)} material announcements in the last {months_back} months.\n"
        categories = set(event['category'] for event in categorized_events)
        category_summary = ", ".join(categories)
        summary += f"Key areas: {category_summary}"

        return {
            'has_material_events': bool(categorized_events),
            'summary': summary,
            'events': sorted(categorized_events, key=lambda x: x['date'], reverse=True)
        }

    except Exception as e:
        return {
            'has_material_events': False,
            'summary': f"Error fetching SENS announcements: {str(e)}",
            'events': []
        }

def parse_sens_content(text_content: str) -> List[Dict]:
    """Parse SENS announcements from text content."""
    # Mock data for testing - replace with actual parsing logic
    # This simulates finding announcements in the text content
    announcements = []

    # Example mock data
    today = datetime.now()
    announcements.append({
        'date': (today - timedelta(days=5)).strftime('%Y-%m-%d'),
        'title': 'Trading Statement and Trading Update',
        'category': 'Financial Results'
    })

    announcements.append({
        'date': (today - timedelta(days=30)).strftime('%Y-%m-%d'),
        'title': 'Director Changes - Appointment of New CFO',
        'category': 'Management Changes'
    })

    announcements.append({
        'date': (today - timedelta(days=60)).strftime('%Y-%m-%d'),
        'title': 'Declaration of Dividend',
        'category': 'Dividends'
    })

    return announcements

def categorize_announcements(announcements: List[Dict]) -> List[Dict]:
    """Categorize announcements based on keywords."""
    keywords = {
        'Financial Results': ['results', 'earnings', 'profit', 'loss', 'performance', 'trading'],
        'Management Changes': ['ceo', 'cfo', 'executive', 'director', 'board', 'appoint', 'resign'],
        'Corporate Actions': ['acquisition', 'merger', 'disposal', 'restructure', 'rights issue'],
        'Dividends': ['dividend', 'distribution'],
        'Regulatory': ['investigation', 'fine', 'penalty', 'compliance'],
        'Strategic': ['strategy', 'expansion', 'contract', 'partnership']
    }

    categorized = []
    for announcement in announcements:
        title_lower = announcement['title'].lower()
        category_found = False

        for category, kwords in keywords.items():
            if any(kw in title_lower for kw in kwords):
                categorized.append({
                    'date': announcement['date'],
                    'category': category,
                    'title': announcement['title']
                })
                category_found = True
                break

        if not category_found:
            # Categorize as Other if no specific category matches
            categorized.append({
                'date': announcement['date'],
                'category': 'Other',
                'title': announcement['title']
            })

    return categorized