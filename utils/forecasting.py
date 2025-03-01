from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from utils.analysis import calculate_portfolio_value

def create_forecast(stock_data, months_ahead=6):
    """Create enhanced linear regression forecast with trend analysis"""
    if stock_data is None or stock_data.empty:
        return pd.Series(), pd.Series(), pd.Series()

    try:
        # Data is already in rands from stock_data.py
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
            periods=months_ahead * 30 + 1,
            freq='D'
        )[1:]

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

        # Make predictions with noise for simulation
        n_simulations = 1000
        predictions = []

        # Calculate prediction error from historical data
        y_pred = model.predict(X_scaled)
        prediction_std = np.std(y - y_pred)

        for _ in range(n_simulations):
            # Add random noise based on historical prediction error
            noise = np.random.normal(0, prediction_std, size=len(X_future))
            sim_predictions = model.predict(X_future_scaled) + noise
            predictions.append(sim_predictions)

        predictions_array = np.array(predictions)

        # Calculate median and confidence intervals
        median_forecast = pd.Series(np.median(predictions_array, axis=0), index=future_dates)
        lower_bound = pd.Series(np.percentile(predictions_array, 2.5, axis=0), index=future_dates)
        upper_bound = pd.Series(np.percentile(predictions_array, 97.5, axis=0), index=future_dates)

        return median_forecast, lower_bound, upper_bound

    except Exception as e:
        print(f"Error in forecast creation: {str(e)}")
        return pd.Series(), pd.Series(), pd.Series()

def calculate_forecast_returns(forecast_data, monthly_investment=100):
    """Calculate potential returns for forecasted period with monthly investments"""
    if forecast_data is None or len(forecast_data) == 0:
        return 0.0, 0.0, 0.0

    try:
        # Create a DataFrame with forecasted prices
        df = pd.DataFrame({'Close': forecast_data})

        # Calculate portfolio value with monthly investments
        portfolio_values = calculate_portfolio_value(df, monthly_investment)

        if len(portfolio_values) == 0:
            return 0.0, 0.0, 0.0

        # Calculate total investment
        total_months = len(portfolio_values)
        total_investment = monthly_investment * total_months

        # Calculate final portfolio value
        final_value = portfolio_values.iloc[-1]

        # Calculate total return
        total_return = final_value - total_investment

        # Calculate return percentage
        return_percentage = ((final_value - total_investment) / total_investment) * 100

        return total_investment, total_return, return_percentage
    except Exception as e:
        print(f"Error calculating forecast returns: {str(e)}")
        return 0.0, 0.0, 0.0

def generate_stock_recommendation(stock_info, forecast_return_percentage):
    """Generate stock recommendation based on various metrics"""
    try:
        score = 0
        reasons = []

        # Analyze P/E Ratio
        pe_ratio = stock_info.get('trailingPE', 0)
        if 0 < pe_ratio <= 15:
            score += 2
            reasons.append("Attractive P/E ratio")
        elif 15 < pe_ratio <= 25:
            score += 1
            reasons.append("Moderate P/E ratio")

        # Analyze Dividend Yield
        div_yield = stock_info.get('dividendYield', 0)
        if div_yield > 0.05:  # 5%
            score += 2
            reasons.append("High dividend yield")
        elif 0.02 <= div_yield <= 0.05:  # 2-5%
            score += 1
            reasons.append("Moderate dividend yield")

        # Analyze forecasted returns
        if forecast_return_percentage > 20:
            score += 2
            reasons.append("Strong forecasted returns")
        elif 10 <= forecast_return_percentage <= 20:
            score += 1
            reasons.append("Moderate forecasted returns")

        # Generate recommendation based on score
        if score >= 4:
            recommendation = "Strong Buy"
        elif score >= 2:
            recommendation = "Buy"
        elif score >= 1:
            recommendation = "Hold"
        else:
            recommendation = "Watch"

        return recommendation, reasons
    except Exception as e:
        print(f"Error generating recommendation: {str(e)}")
        return "Unable to generate recommendation", []