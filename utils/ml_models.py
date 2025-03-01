import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')

def prepare_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Create technical indicators and features for ML models.
    """
    df = data.copy()
    
    # Basic price features
    df['Returns'] = df['Close'].pct_change()
    df['Volume_Change'] = df['Volume'].pct_change()
    
    # Moving averages
    for window in [5, 10, 20, 50]:
        df[f'MA_{window}'] = df['Close'].rolling(window=window).mean()
        df[f'Volume_MA_{window}'] = df['Volume'].rolling(window=window).mean()
    
    # Volatility
    df['Volatility'] = df['Returns'].rolling(window=20).std()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Upper'] = df['BB_Middle'] + 2 * df['Close'].rolling(window=20).std()
    df['BB_Lower'] = df['BB_Middle'] - 2 * df['Close'].rolling(window=20).std()
    
    # Price position
    df['Price_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
    
    # Drop NaN values
    df = df.dropna()
    
    return df

def create_sequences(data: pd.DataFrame, seq_length: int = 30) -> tuple:
    """
    Create sequences for time series prediction.
    """
    feature_columns = ['Returns', 'Volume_Change', 'Volatility', 'RSI', 'MACD', 
                      'Price_Position'] + \
                     [f'MA_{window}' for window in [5, 10, 20, 50]] + \
                     [f'Volume_MA_{window}' for window in [5, 10, 20, 50]]
    
    X = data[feature_columns].values
    y = data['Close'].values
    
    X_sequences = []
    y_sequences = []
    
    for i in range(len(data) - seq_length):
        X_sequences.append(X[i:(i + seq_length)])
        y_sequences.append(y[i + seq_length])
    
    return np.array(X_sequences), np.array(y_sequences)

def train_predict_rf(data: pd.DataFrame, horizon: int = 30, num_simulations: int = 100) -> tuple:
    """
    Train Random Forest model and generate predictions with confidence intervals.
    """
    # Prepare features
    df = prepare_features(data)
    
    # Create sequences
    X_seq, y_seq = create_sequences(df)
    
    # Split data
    split_idx = int(len(X_seq) * 0.8)
    X_train = X_seq[:split_idx]
    y_train = y_seq[:split_idx]
    
    # Scale features
    scaler = StandardScaler()
    X_train_reshaped = X_train.reshape(X_train.shape[0], -1)
    X_train_scaled = scaler.fit_transform(X_train_reshaped)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Generate future predictions
    last_sequence = X_seq[-1]
    predictions = []
    prediction_intervals = []
    
    current_sequence = last_sequence.copy()
    
    for _ in range(horizon):
        # Reshape and scale
        current_scaled = scaler.transform(current_sequence.reshape(1, -1))
        
        # Generate predictions for all trees
        tree_predictions = []
        for estimator in model.estimators_:
            pred = estimator.predict(current_scaled)
            tree_predictions.append(pred[0])
        
        # Calculate mean and confidence intervals
        mean_pred = np.mean(tree_predictions)
        confidence_interval = np.percentile(tree_predictions, [5, 95])
        
        predictions.append(mean_pred)
        prediction_intervals.append(confidence_interval)
        
        # Update sequence for next prediction
        new_features = prepare_features(pd.DataFrame({
            'Close': [mean_pred],
            'Volume': [data['Volume'].mean()]  # Use average volume
        }))
        
        if not new_features.empty:
            current_sequence = np.roll(current_sequence, -1, axis=0)
            current_sequence[-1] = X_seq[-1][-1]  # Use last known features
    
    return np.array(predictions), np.array(prediction_intervals)

def generate_ml_forecast(stock_data: pd.DataFrame, months_ahead: int = 6) -> tuple:
    """
    Generate ML-based forecasts with confidence intervals.
    """
    # Convert months to trading days (approximately 21 trading days per month)
    horizon = months_ahead * 21
    
    try:
        # Generate predictions
        predictions, intervals = train_predict_rf(stock_data, horizon=horizon)
        
        # Create dates for forecasted values
        last_date = stock_data.index[-1]
        forecast_dates = pd.date_range(start=last_date, periods=horizon + 1, freq='B')[1:]
        
        # Create forecast series
        forecast = pd.Series(predictions, index=forecast_dates)
        lower_bound = pd.Series(intervals[:, 0], index=forecast_dates)
        upper_bound = pd.Series(intervals[:, 1], index=forecast_dates)
        
        return forecast, lower_bound, upper_bound
        
    except Exception as e:
        print(f"Error generating ML forecast: {str(e)}")
        return pd.Series(), pd.Series(), pd.Series()
