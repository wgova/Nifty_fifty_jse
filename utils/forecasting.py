from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def create_forecast(stock_data, months_ahead=6):
    """Create enhanced linear regression forecast with trend analysis"""
    if stock_data is None or stock_data.empty:
        return pd.Series()

    try:
        # Prepare data with additional features
        df = stock_data.copy()
        df['Days'] = range(len(df))

        # Add time-based features
        df['Month'] = df.index.month
        df['Year'] = df.index.year
        df['DayOfWeek'] = df.index.dayofweek

        # Calculate rolling statistics
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
        df['Volatility'] = df['Close'].rolling(window=30).std()

        # Fill missing values from rolling calculations
        df = df.fillna(method='bfill')

        # Prepare features for training
        features = ['Days', 'Month', 'DayOfWeek', 'MA50', 'MA200', 'Volatility']
        X = df[features]
        y = df['Close']

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train model
        model = LinearRegression()
        model.fit(X_scaled, y)

        # Create future dates
        last_date = df.index[-1]
        future_dates = pd.date_range(
            start=last_date,
            periods=months_ahead * 30 + 1,  # Add 1 to include the last date
            freq='D'
        )[1:]  # Remove the first date to avoid overlap

        # Create future features
        future_df = pd.DataFrame(index=future_dates)
        future_df['Days'] = range(len(df), len(df) + len(future_dates))
        future_df['Month'] = future_dates.month
        future_df['Year'] = future_dates.year
        future_df['DayOfWeek'] = future_dates.dayofweek

        # Initialize MA and Volatility with last known values
        future_df['MA50'] = df['MA50'].iloc[-1]
        future_df['MA200'] = df['MA200'].iloc[-1]
        future_df['Volatility'] = df['Volatility'].iloc[-1]

        # Scale future features
        X_future = future_df[features]
        X_future_scaled = scaler.transform(X_future)

        # Make predictions
        future_predictions = model.predict(X_future_scaled)

        # Create prediction series
        predictions = pd.Series(future_predictions, index=future_dates)

        return predictions

    except Exception as e:
        print(f"Error in forecast creation: {str(e)}")
        return pd.Series()

def calculate_confidence_intervals(predictions, confidence_level=0.95):
    """Calculate confidence intervals using enhanced method"""
    if predictions is None or len(predictions) == 0:
        return pd.Series(), pd.Series()

    try:
        # Calculate rolling standard deviation for dynamic intervals
        rolling_std = predictions.rolling(window=30, min_periods=1).std()

        # Use t-distribution for more accurate intervals
        from scipy import stats
        t_value = stats.t.ppf((1 + confidence_level) / 2, len(predictions) - 1)

        # Calculate margins that increase with time
        time_factor = np.sqrt(np.arange(1, len(predictions) + 1) / len(predictions))
        margin = t_value * rolling_std * time_factor

        upper = predictions + margin
        lower = predictions - margin

        # Ensure lower bound doesn't go negative
        lower = lower.clip(lower=0)

        return upper, lower
    except Exception as e:
        print(f"Error in confidence interval calculation: {str(e)}")
        return pd.Series(), pd.Series()