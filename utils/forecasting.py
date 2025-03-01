from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd

def create_forecast(stock_data, months_ahead=6):
    """Create simple linear regression forecast"""
    if stock_data is None or stock_data.empty:
        return pd.Series()

    try:
        # Prepare data
        df = stock_data.copy()
        df['Prediction'] = df['Close']
        df['Days'] = range(len(df))

        # Train model
        X = df[['Days']]
        y = df['Close']
        model = LinearRegression()
        model.fit(X, y)

        # Create future dates
        last_date = df.index[-1]
        future_dates = pd.date_range(
            start=last_date,
            periods=months_ahead * 30,
            freq='D'
        )

        # Make predictions
        future_X = pd.DataFrame({'Days': range(len(df), len(df) + len(future_dates))})
        future_predictions = model.predict(future_X)

        return pd.Series(future_predictions, index=future_dates)
    except Exception as e:
        print(f"Error in forecast creation: {str(e)}")
        return pd.Series()

def calculate_confidence_intervals(predictions, std_dev=2):
    """Calculate confidence intervals for predictions"""
    if predictions is None or len(predictions) == 0:
        return pd.Series(), pd.Series()

    try:
        prediction_std = predictions.std()
        upper = predictions + (std_dev * prediction_std)
        lower = predictions - (std_dev * prediction_std)
        return upper, lower
    except Exception as e:
        print(f"Error in confidence interval calculation: {str(e)}")
        return pd.Series(), pd.Series()