import re
import backtrader as bt
import pandas as pd
import numpy as np

# Useful when working with multiple files (e.g., AAPL.csv or TSLA.csv) to get the ticker.
def extract_ticker_from_path(file_path: str) -> str:
    """
    Extracts the ticker symbol from the given file path.
    """
    match = re.search(r"/([^/]+)\.csv$", file_path)
    if match:
        return match.group(1)
    else:
        raise ValueError("Ticker symbol not found in the file path")
    

def calculate_indicators_bt(data):
    """
    Calculate and return a dictionary of technical indicators for a given Backtrader data feed.

    Parameters:
    - data (bt.feeds.PandasData): Backtrader data feed.

    Returns:
    - dict: Dictionary containing calculated indicators.
    """
    indicators = {}
    
    indicators["Open"] = data.open
    indicators["High"] = data.high
    indicators["Low"] = data.low
    indicators["Volume"] = data.volume
    indicators["Close"] = data.close

    # Votatility
    indicators["Price_Change"] = data.close - data.open
    indicators["Votatility"] = (data.high - data.low) / data.low

    # Simple Moving Averages (SMA)
    indicators['SMA_10'] = bt.indicators.SimpleMovingAverage(data.close, period=10)
    indicators['SMA_50'] = bt.indicators.SimpleMovingAverage(data.close, period=50)
    
    # Momentum (difference between current and previous close)
    indicators['Momentum'] = data.close - data.close(-10)
    
    
    # # Exponential Moving Averages (EMA)
    # indicators['EMA_10'] = bt.indicators.ExponentialMovingAverage(data.close, period=10)
    # indicators['EMA_50'] = bt.indicators.ExponentialMovingAverage(data.close, period=50)
    
    # Relative Strength Index (RSI)
    indicators['RSI'] = bt.indicators.RelativeStrengthIndex(data.close, period=14)
    
    # Moving Average Convergence Divergence (MACD)
    macd = bt.indicators.MACD(data.close)
    indicators['MACD'] = macd.macd
    # indicators['MACD_Signal'] = macd.signal
    
    # Bollinger Bands
    bb = bt.indicators.BollingerBands(data.close, period=20, devfactor=2)
    indicators['BB_Middle'] = bb.lines.mid
    indicators['BB_Upper'] = bb.lines.top
    indicators['BB_Lower'] = bb.lines.bot
    
    # # Average True Range (ATR)
    # indicators['ATR'] = bt.indicators.AverageTrueRange(data, period=14)
    
    # # Rate of Change (ROC)
    # indicators['ROC'] = bt.indicators.RateOfChange(data.close, period=10)
    
    # # Stochastic Oscillator
    # stoch = bt.indicators.Stochastic(data, period=14)
    # indicators['Stochastic'] = stoch.percD  # Or use stoch.percK for %K line
    
    # # Lagged values (previous closing values)
    # indicators['Lag_1'] = data.close(-1)
    # indicators['Lag_5'] = data.close(-5)
    # indicators['Lag_10'] = data.close(-10)
    
    # # Rolling Standard Deviation
    # indicators['Rolling_Std_10'] = bt.indicators.StandardDeviation(data.close, period=10)
    # indicators['Rolling_Std_30'] = bt.indicators.StandardDeviation(data.close, period=30)
    
    return indicators


def calculate_indicators_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates technical indicators and adds them as columns to the input DataFrame.
    
    Parameters:
    - df (pd.DataFrame): DataFrame with at least 'Close', 'High', and 'Low' columns.
    
    Returns:
    - pd.DataFrame: DataFrame with new columns for various technical indicators.
    """
    # Votatility
    df["Price_Change"] = df["Close"] - df["Open"]
    df["Votatility"] = (df["High"] - df["Low"]) / df["Low"]

    # Simple Moving Averages (SMA)
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()

    # Exponential Moving Averages (EMA)
    df['EMA_10'] = df['Close'].ewm(span=10, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()

    # Momentum Indicator
    df['Momentum'] = df['Close'] - df['Close'].shift(10)

    # Relative Strength Index (RSI)
    window_length = 14
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window_length, min_periods=1).mean()
    avg_loss = loss.rolling(window=window_length, min_periods=1).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Moving Average Convergence Divergence (MACD)
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Upper'] = df['BB_Middle'] + 2 * df['Close'].rolling(window=20).std()
    df['BB_Lower'] = df['BB_Middle'] - 2 * df['Close'].rolling(window=20).std()

    # Average True Range (ATR)
    df['High_Low'] = df['High'] - df['Low']
    df['High_Close'] = abs(df['High'] - df['Close'].shift())
    df['Low_Close'] = abs(df['Low'] - df['Close'].shift())
    df['True_Range'] = df[['High_Low', 'High_Close', 'Low_Close']].max(axis=1)
    df['ATR'] = df['True_Range'].rolling(window=14).mean()

    # Rate of Change (ROC)
    df['ROC'] = df['Close'].pct_change(periods=10)

    # Stochastic Oscillator
    low_min = df['Low'].rolling(window=14).min()
    high_max = df['High'].rolling(window=14).max()
    df['Stochastic'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))

    # Lagged Returns
    df['Lag_1'] = df['Close'].pct_change(1)
    df['Lag_5'] = df['Close'].pct_change(5)
    df['Lag_10'] = df['Close'].pct_change(10)

    # Rolling Standard Deviation (Volatility)
    df['Rolling_Std_10'] = df['Close'].rolling(window=10).std()
    df['Rolling_Std_30'] = df['Close'].rolling(window=30).std()

    # Drop rows with NaN values due to rolling calculations
    df.dropna(inplace=True)

    return df
