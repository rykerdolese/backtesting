import streamlit as st
from datetime import datetime
from trading.trader import AITrader
from trading.base_strategy import *
from trading.traditional_strategies import (
    BuyHold, NaiveMovingAverage, CrossMovingAverage,
    BollingerBands, Momentum, NaiveeRSI,
    RsiBollingerBands, NaiveRateOfChange, ROCMovingAverage,
    FearGreed, PutCall, VIX, 
)
from trading.ai_strategies import (MLTradingStrategy, RNNStrategy)
import mpld3
import streamlit.components.v1 as components
import os

# page config
st.set_page_config(
    page_title="Backtesting",
    page_icon="📈",
)

# content only for backtesting page
# Title of the page
st.title("Backtesting Page")

st.write("##### Set the Configuration to run the backtest.")

# Sidebar for AI Trader Configuration
st.sidebar.title("AI Trader Configuration")

# Initial Cash Input
initial_cash = st.sidebar.number_input("Initial Cash ($)", min_value=1000, max_value=10_000_000, value=1_000_000)

# Commission Rate Input
commission_rate = st.sidebar.number_input("Commission Rate (%)", min_value=0.0, max_value=1.0, value=0.1425) / 100


# Sizer Percentage
position_sizer = st.sidebar.number_input("Position Sizer (%)", min_value=1, max_value=100, value=95)

# Define list of stock tickers
available_stocks = [
    "AAPL", "MSFT", "NVDA", "GOOG", "AMZN", "META",
    "BRK-B", "LLY", "AVGO", "TSLA", "WMT", "JPM", 
    "V", "UNH", "XOM", "ORCL", "MA", "HD", "PG", 
    "COST", "^SPX"
]

# Dropdown menu for selecting a stock ticker
stock_ticker = st.sidebar.selectbox("Select Stock Ticker", available_stocks)

# Define strategy categories
strategy_categories = {
    "Traditional Strategies": {
        "Buy and Hold": (BuyHold, {}),
        "Naive Moving Average": (NaiveMovingAverage, {"sma_period": 30}),
        "Cross Moving Average": (CrossMovingAverage, {"fast": 5, "slow": 37}),
        "Bollinger Bands": (BollingerBands, {"period": 20, "devfactor": 2}),
        "Momentum": (Momentum, {"sma_period": 50, "momentum_period": 14}),
        "Naive RSI": (NaiveeRSI, {"rsi_period": 14, "oversold": 30, "overbought": 70}),
        "RSI with Bollinger Bands": (RsiBollingerBands, {"rsi_period": 14, "bb_period": 20, "bb_dev": 2, "oversold": 30, "overbought": 70}),
        "Naive Rate of Change (ROC)": (NaiveRateOfChange, {"period": 20, "threshold": 0.08}),
        "ROC with Moving Average": (ROCMovingAverage, {"roc_period": 12, "fast_ma_period": 10, "slow_ma_period": 30}),
        "FearGreed": (FearGreed, {}),
        "PutCall": (PutCall, {}),
        "Volatility Index": (VIX, {}),
    },
    "AI-Powered Strategies": {
        "Logistic Regression": (MLTradingStrategy, {"model_name": "Logistic_Regression"}),
        "Gradient Boosting": (MLTradingStrategy, {"model_name": "Gradient_Boosting"}),
        "Recurrent Neural Network (RNN)": (RNNStrategy, {}),
    },
}

# Sidebar dropdown for strategy category
selected_category = st.sidebar.selectbox("Choose Strategy Category", list(strategy_categories.keys()))

# Display strategies based on the selected category
strategies = strategy_categories[selected_category]
selected_strategy_name = st.sidebar.selectbox("Choose Strategy", list(strategies.keys()))
selected_strategy, default_params = strategies[selected_strategy_name]

# Sidebar inputs for the selected strategy's parameters
strategy_params = {}
if selected_category == "Traditional Strategies":
    if selected_strategy_name == "Naive Moving Average":
        strategy_params['sma_period'] = st.sidebar.number_input("SMA Period", min_value=1, max_value=200, value=default_params["sma_period"])
    elif selected_strategy_name == "Cross Moving Average":
        strategy_params['fast'] = st.sidebar.number_input("Fast SMA Period", min_value=1, max_value=200, value=default_params["fast"])
        strategy_params['slow'] = st.sidebar.number_input("Slow SMA Period", min_value=1, max_value=200, value=default_params["slow"])
    elif selected_strategy_name == "Bollinger Bands":
        strategy_params['period'] = st.sidebar.number_input("Bollinger Period", min_value=1, max_value=200, value=default_params["period"])
        strategy_params['devfactor'] = st.sidebar.number_input("Deviation Factor", min_value=1, max_value=3, value=default_params["devfactor"])
    elif selected_strategy_name == "Momentum":
        strategy_params['sma_period'] = st.sidebar.number_input("SMA Period", min_value=1, max_value=200, value=default_params["sma_period"])
        strategy_params['momentum_period'] = st.sidebar.number_input("Momentum Period", min_value=1, max_value=200, value=default_params["momentum_period"])
    elif selected_strategy_name == "Naive RSI":
        strategy_params['rsi_period'] = st.sidebar.number_input("RSI Period", min_value=1, max_value=200, value=default_params["rsi_period"])
        strategy_params['oversold'] = st.sidebar.number_input("Oversold Threshold", min_value=1, max_value=100, value=default_params["oversold"])
        strategy_params['overbought'] = st.sidebar.number_input("Overbought Threshold", min_value=1, max_value=100, value=default_params["overbought"])
    elif selected_strategy_name == "RSI with Bollinger Bands":
        strategy_params['rsi_period'] = st.sidebar.number_input("RSI Period", min_value=1, max_value=200, value=default_params["rsi_period"])
        strategy_params['bb_period'] = st.sidebar.number_input("Bollinger Period", min_value=1, max_value=200, value=default_params["bb_period"])
        strategy_params['bb_dev'] = st.sidebar.number_input("Bollinger Deviation", min_value=1, max_value=5, value=default_params["bb_dev"])
        strategy_params['oversold'] = st.sidebar.number_input("Oversold Threshold", min_value=1, max_value=100, value=default_params["oversold"])
        strategy_params['overbought'] = st.sidebar.number_input("Overbought Threshold", min_value=1, max_value=100, value=default_params["overbought"])
    elif selected_strategy_name == "Naive Rate of Change (ROC)":
        strategy_params['period'] = st.sidebar.number_input("ROC Period", min_value=1, max_value=200, value=default_params["period"])
        strategy_params['threshold'] = st.sidebar.number_input("ROC Threshold", min_value=0.0, max_value=1.0, value=default_params["threshold"])
    elif selected_strategy_name == "ROC with Moving Average":
        strategy_params['roc_period'] = st.sidebar.number_input("ROC Period", min_value=1, max_value=200, value=default_params["roc_period"])
        strategy_params['fast_ma_period'] = st.sidebar.number_input("Fast MA Period", min_value=1, max_value=200, value=default_params["fast_ma_period"])
        strategy_params['slow_ma_period'] = st.sidebar.number_input("Slow MA Period", min_value=1, max_value=200, value=default_params["slow_ma_period"])
else:
    if selected_strategy_name in ["Logistic Regression", "Gradient Boosting"]:
        strategy_params['model_name'] = selected_strategy_name.replace(" ", "_")
        strategy_params['stock_ticker'] = stock_ticker

# Define the minimum and maximum date range for backtesting
min_date = datetime(2014, 1, 1)
max_date = datetime(2024, 10, 31)

# Date inputs with limited range
start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1), min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", datetime(2024, 10, 1), min_value=min_date, max_value=max_date)


# Button to start the backtest
# Run Backtest
if st.sidebar.button("Run Backtest"):
    trader = AITrader(
        cash = initial_cash,
        commission = commission_rate,
        size = position_sizer,
        start_date=start_date,
        end_date=end_date)

    # Check if model and scaler files exist for AI strategies
    if selected_strategy_name in ["Logistic Regression", "Gradient Boosting"]:
        model_path = f"./model/{stock_ticker}_{strategy_params['model_name']}_model.pkl"
        scaler_path = f"./model/{stock_ticker}_scaler.pkl"

        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            st.error(f"Model or scaler file for {stock_ticker} not found. Train the model first.")
        else:
            trader.add_strategy(MLTradingStrategy, strategy_params)
    elif selected_strategy_name == "Recurrent Neural Network (RNN)":
        if not os.path.exists(f"./data/us_stock/predictions/{stock_ticker}.csv"):
            st.error(f"Data for {stock_ticker} not found. Train the model first.")
        else:
            trader.add_strategy(RNNStrategy, {})
    else:
        trader.add_strategy(selected_strategy, strategy_params)

    # Execute backtest
    try:
        metrics = trader.run(1, stock_ticker=stock_ticker)
        st.write("### Backtest Results")
     
        metrics_list = list(metrics.items())
        first_row_metrics = metrics_list[:1]  # First three metrics
        second_row_metrics = metrics_list[1:]  # Remaining metrics

        # Display the first row of metrics
        if first_row_metrics:
            first_row = st.columns(len(first_row_metrics))
            for col, (metric, value) in zip(first_row, first_row_metrics):
                col.metric(label=metric, value=value)

        # Display the second row of metrics
        if second_row_metrics:
            second_row = st.columns(len(second_row_metrics))
            for col, (metric, value) in zip(second_row, second_row_metrics):
                col.metric(label=metric, value=value)

        # Display log
        with open("./log/trading_log.txt", "r") as log_file:
            st.text_area("Log File Content", log_file.read(), height=300)

        # Display performance chart
        st.write("### Backtest Performance Chart")
        st.pyplot(trader.plot())
    except ValueError as e:
        st.error(str(e))
    
    
