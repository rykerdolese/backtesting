from trading.base_strategy import *
import joblib
from trading.utils import calculate_indicators_bt

selected_features = ['Close', 'SMA_10', 'SMA_50', 'Momentum', 'RSI', 'MACD', 'BB_Middle', 'BB_Upper', 'BB_Lower']

class MLTradingStrategy(BaseStrategy):
    """
    A strategy that uses a machine learning model to predict buy/sell signals,
    specific to the selected stock ticker.
    """
    params = dict(
        model_name='Logistic_Regression',  # Choose between 'logistic' and 'gradient_boosting'
        stock_ticker='AAPL',  # Default stock ticker
    )

    def __init__(self):
        if self.params.model_name not in ['Logistic_Regression', 'Gradient_Boosting']:
            raise ValueError("Unsupported model name. Choose 'logistic' or 'gradient_boosting'.")

        self.model_name = self.params.model_name
        self.stock_ticker = self.params.stock_ticker

        model_path = f"./model/{self.stock_ticker}_{self.model_name}_model.pkl"
        scaler_path = f"./model/{self.stock_ticker}_scaler.pkl"

        self.scaler = joblib.load(scaler_path)
        self.model = joblib.load(model_path)

        self.indicators = calculate_indicators_bt(self.data)
        self.selected_features = selected_features  

    def next(self):
        features = [[self.indicators[feature][0] for feature in self.selected_features]]
        features = self.scaler.transform(features)
        prediction = self.model.predict(features)[0]

        if not self.position:
            if prediction == 1:
                self.buy()
                self.log(f'BUY CREATE {self.data.close[0]:.2f}')
        else:
            if prediction == 0:
                self.sell()
                self.log(f'SELL CREATE {self.data.close[0]:.2f}')


class RNNStrategy(BaseStrategy):
    """
    Backtrader strategy using RNN predictions.
    """
    def __init__(self):
        self.dataclose = self.data.close
        self.predictions = self.data.predictions

    def next(self):
        if self.position.size == 0:
            if self.predictions[0] > self.dataclose[0] * (1):
                self.buy()
                self.log(f'BUY CREATE {self.data.close[0]:.2f}')
        else:
            if self.predictions[0] < self.dataclose[0] * (1):
                self.sell()
                self.log(f'SELL CREATE {self.data.close[0]:.2f}')



