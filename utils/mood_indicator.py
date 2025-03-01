import numpy as np
from typing import Dict, Tuple

def calculate_stock_mood(
    price_data: pd.DataFrame,
    metrics: Dict
) -> Tuple[str, str, float]:
    """
    Calculate stock mood based on various technical and fundamental indicators.
    Returns emoji, mood description, and confidence score.
    """
    try:
        # Calculate price trend
        recent_prices = price_data['Close'].tail(20)  # Last 20 days
        price_change = ((recent_prices.iloc[-1] - recent_prices.iloc[0]) / 
                       recent_prices.iloc[0]) * 100
        
        # Calculate volatility
        volatility = recent_prices.pct_change().std() * np.sqrt(252) * 100
        
        # Volume trend
        recent_volume = price_data['Volume'].tail(20)
        volume_change = ((recent_volume.iloc[-1] - recent_volume.iloc[0]) / 
                        recent_volume.iloc[0]) * 100
        
        # Get fundamental metrics
        pe_ratio = metrics.get('P/E Ratio', 'N/A')
        if isinstance(pe_ratio, str):
            pe_ratio = 15  # Default to market average if N/A
            
        # Define mood thresholds
        moods = {
            'very_bullish': {
                'emoji': '🚀',
                'description': 'Extremely Bullish',
                'conditions': lambda: (
                    price_change > 10 and 
                    volume_change > 0 and 
                    volatility < 30 and 
                    pe_ratio < 25
                )
            },
            'bullish': {
                'emoji': '😊',
                'description': 'Bullish',
                'conditions': lambda: (
                    price_change > 5 and 
                    volume_change > -10
                )
            },
            'neutral_positive': {
                'emoji': '🙂',
                'description': 'Mildly Positive',
                'conditions': lambda: (
                    price_change > 0 and 
                    volume_change > -20
                )
            },
            'neutral': {
                'emoji': '😐',
                'description': 'Neutral',
                'conditions': lambda: (
                    abs(price_change) < 3 and 
                    abs(volume_change) < 20
                )
            },
            'neutral_negative': {
                'emoji': '🙁',
                'description': 'Mildly Negative',
                'conditions': lambda: (
                    price_change < 0 and 
                    price_change > -5
                )
            },
            'bearish': {
                'emoji': '😟',
                'description': 'Bearish',
                'conditions': lambda: (
                    price_change < -5 or 
                    volume_change < -20
                )
            },
            'very_bearish': {
                'emoji': '🆘',
                'description': 'Extremely Bearish',
                'conditions': lambda: (
                    price_change < -10 and 
                    volume_change < -20 and 
                    volatility > 40
                )
            }
        }

        # Calculate confidence score based on how many indicators align
        confidence_factors = [
            1 if abs(price_change) > 5 else 0.5,
            1 if abs(volume_change) > 10 else 0.5,
            1 if volatility < 30 else 0.5,
            1 if 10 < pe_ratio < 20 else 0.5
        ]
        confidence = sum(confidence_factors) / len(confidence_factors)

        # Determine mood
        for mood_name, mood_data in moods.items():
            if mood_data['conditions']():
                return (
                    mood_data['emoji'],
                    mood_data['description'],
                    confidence
                )

        # Default to neutral if no conditions met
        return '😐', 'Neutral', 0.5

    except Exception as e:
        print(f"Error calculating stock mood: {str(e)}")
        return '❓', 'Unknown', 0.0

def get_mood_explanation(
    price_change: float,
    volume_change: float,
    volatility: float,
    pe_ratio: float
) -> str:
    """Generate human-readable explanation for the mood indicator."""
    explanation = []
    
    # Price trend explanation
    if abs(price_change) > 0:
        explanation.append(
            f"Price {'increased' if price_change > 0 else 'decreased'} "
            f"by {abs(price_change):.1f}%"
        )
    
    # Volume trend
    if abs(volume_change) > 10:
        explanation.append(
            f"Trading volume {'increased' if volume_change > 0 else 'decreased'} "
            f"significantly"
        )
    
    # Volatility
    if volatility > 30:
        explanation.append("Stock showing high volatility")
    elif volatility < 15:
        explanation.append("Stock showing low volatility")
    
    # P/E context
    if pe_ratio < 15:
        explanation.append("P/E ratio suggests potential undervaluation")
    elif pe_ratio > 25:
        explanation.append("P/E ratio suggests potential overvaluation")
    
    return " • ".join(explanation)
