import streamlit as st
from datetime import datetime
import pandas as pd
import os
from trading.trader import AITrader
from trading.traditional_strategies import (
    BuyHold, NaiveMovingAverage, CrossMovingAverage,
    BollingerBands, Momentum, NaiveeRSI,
    RsiBollingerBands, NaiveRateOfChange, ROCMovingAverage,
    FearGreed, PutCall, VIX
)
from trading.ai_strategies import (MLTradingStrategy, RNNStrategy, DQNStrategy)
from trading.rl_module import *

# Page configuration
st.set_page_config(page_title="Backtest Comparison", page_icon="📊")

# Title and description
st.title("Backtest Comparison Tool")
st.write("##### Configure and compare two backtests side by side.")

# Function to configure a single backtest
def configure_backtest(label: str):
    st.sidebar.subheader(f"{label} Configuration")
    config = {}
    config["initial_cash"] = st.sidebar.number_input(f"{label} - Initial Cash ($)", min_value=1000, max_value=10_000_000, value=1_000_000)
    config["commission_rate"] = st.sidebar.number_input(f"{label} - Commission Rate (%)", min_value=0.0, max_value=1.0, value=0.1425) / 100
    config["position_sizer"] = st.sidebar.number_input(f"{label} - Position Sizer (%)", min_value=1, max_value=100, value=95)

    # Stock Ticker
    available_stocks = [
        "AAPL", "MSFT", "NVDA", "GOOG", "AMZN", "META",
        "BRK-B", "LLY", "AVGO", "TSLA", "WMT", "JPM",
        "V", "UNH", "XOM", "ORCL", "MA", "HD", "PG",
        "COST", "^SPX"
    ]
    config["stock_ticker"] = st.sidebar.selectbox(f"{label} - Select Stock Ticker", available_stocks)

    # Strategy selection
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
            "Recurrent Neural Network (RNN)": (RNNStrategy, {}),
            "Deep Q Network (DQN)": (DQNStrategy, {}),
        },
    }

    config["selected_category"] = st.sidebar.selectbox(f"{label} - Choose Strategy Category", list(strategy_categories.keys()))
    strategies = strategy_categories[config["selected_category"]]
    config["selected_strategy_name"] = st.sidebar.selectbox(f"{label} - Choose Strategy", list(strategies.keys()))
    config["selected_strategy"], default_params = strategies[config["selected_strategy_name"]]

    # Parameters for selected strategy
    config["strategy_params"] = {}
    if config["selected_category"] == "Traditional Strategies":
        if config["selected_strategy_name"] == "Naive Moving Average":
            config["strategy_params"]['sma_period'] = st.sidebar.number_input("SMA Period", min_value=1, max_value=200, value=default_params["sma_period"])
        elif config["selected_strategy_name"] == "Cross Moving Average":
            config["strategy_params"]['fast'] = st.sidebar.number_input("Fast SMA Period", min_value=1, max_value=200, value=default_params["fast"])
            config["strategy_params"]['slow'] = st.sidebar.number_input("Slow SMA Period", min_value=1, max_value=200, value=default_params["slow"])
        elif config["selected_strategy_name"] == "Bollinger Bands":
            config["strategy_params"]['period'] = st.sidebar.number_input("Bollinger Period", min_value=1, max_value=200, value=default_params["period"])
            config["strategy_params"]['devfactor'] = st.sidebar.number_input("Deviation Factor", min_value=1, max_value=3, value=default_params["devfactor"])
        elif config["selected_strategy_name"] == "Momentum":
            config["strategy_params"]['sma_period'] = st.sidebar.number_input("SMA Period", min_value=1, max_value=200, value=default_params["sma_period"])
            config["strategy_params"]['momentum_period'] = st.sidebar.number_input("Momentum Period", min_value=1, max_value=200, value=default_params["momentum_period"])
        elif config["selected_strategy_name"] == "Naive RSI":
            config["strategy_params"]['rsi_period'] = st.sidebar.number_input("RSI Period", min_value=1, max_value=200, value=default_params["rsi_period"])
            config["strategy_params"]['oversold'] = st.sidebar.number_input("Oversold Threshold", min_value=1, max_value=100, value=default_params["oversold"])
            config["strategy_params"]['overbought'] = st.sidebar.number_input("Overbought Threshold", min_value=1, max_value=100, value=default_params["overbought"])
        elif config["selected_strategy_name"] == "RSI with Bollinger Bands":
            config["strategy_params"]['rsi_period'] = st.sidebar.number_input("RSI Period", min_value=1, max_value=200, value=default_params["rsi_period"])
            config["strategy_params"]['bb_period'] = st.sidebar.number_input("Bollinger Period", min_value=1, max_value=200, value=default_params["bb_period"])
            config["strategy_params"]['bb_dev'] = st.sidebar.number_input("Bollinger Deviation", min_value=1, max_value=5, value=default_params["bb_dev"])
            config["strategy_params"]['oversold'] = st.sidebar.number_input("Oversold Threshold", min_value=1, max_value=100, value=default_params["oversold"])
            config["strategy_params"]['overbought'] = st.sidebar.number_input("Overbought Threshold", min_value=1, max_value=100, value=default_params["overbought"])
        elif config["selected_strategy_name"] == "Naive Rate of Change (ROC)":
            config["strategy_params"]['period'] = st.sidebar.number_input("ROC Period", min_value=1, max_value=200, value=default_params["period"])
            config["strategy_params"]['threshold'] = st.sidebar.number_input("ROC Threshold", min_value=0.0, max_value=1.0, value=default_params["threshold"])
        elif config["selected_strategy_name"] == "ROC with Moving Average":
            config["strategy_params"]['roc_period'] = st.sidebar.number_input("ROC Period", min_value=1, max_value=200, value=default_params["roc_period"])
            config["strategy_params"]['fast_ma_period'] = st.sidebar.number_input("Fast MA Period", min_value=1, max_value=200, value=default_params["fast_ma_period"])
            config["strategy_params"]['slow_ma_period'] = st.sidebar.number_input("Slow MA Period", min_value=1, max_value=200, value=default_params["slow_ma_period"])
    else:
        if config["selected_strategy_name"] in ["Logistic Regression", "Gradient Boosting"]:
            config["strategy_params"]['model_name'] = config["selected_strategy_name"].replace(" ", "_")
            config["strategy_params"]['stock_ticker'] = config["stock_ticker"]

    # Date inputs
    min_date, max_date = datetime(2014, 1, 1), datetime(2024, 10, 31)
    config["start_date"] = st.sidebar.date_input(f"{label} - Start Date", datetime(2024, 1, 1), min_value=min_date, max_value=max_date)
    config["end_date"] = st.sidebar.date_input(f"{label} - End Date", datetime(2024, 10, 1), min_value=min_date, max_value=max_date)

    return config

# Configure two backtests
config_1 = configure_backtest("Configuration 1")
config_2 = configure_backtest("Configuration 2")

# Button to run and compare backtests
if st.sidebar.button("Run and Compare Backtests"):

    # Function to run a backtest
    def run_backtest(config):
        # Initialize the AITrader instance with user-defined configurations
        trader = AITrader(
            cash=config["initial_cash"],
            commission=config["commission_rate"],
            start_date=config["start_date"],
            end_date=config["end_date"],
        )

        # Add the appropriate strategy
        if config["selected_strategy_name"] == "Logistic Regression":
            # Ensure AI model and scaler files exist
            model_path = f"./model/{config['stock_ticker']}_{config['strategy_params'].get('model_name')}_model.pkl"
            scaler_path = f"./model/{config['stock_ticker']}_scaler.pkl"

            if not os.path.exists(model_path) or not os.path.exists(scaler_path):
                st.error(f"Required model or scaler files for {config['stock_ticker']} not found. Train the model first.")
                return None, None

            # Add AI-powered strategy with model-specific parameters
            trader.add_strategy(config["selected_strategy"], params=config["strategy_params"])
        elif config["selected_strategy_name"] == "Recurrent Neural Network (RNN)":
            if not os.path.exists(f"./data/us_stock/predictions/{config['stock_ticker']}.csv"):
                st.error(f"Data for {config['stock_ticker']} not found. Train the model first.")
            else:
                trader.add_strategy(RNNStrategy, {})
        elif config["selected_strategy_name"] == "Deep Q Network (DQN)":
            # Load the trained model
            model_path = f"./model/{config['stock_ticker']}_DQN_model.pth"
            if not os.path.exists(model_path):
                st.error(f"Model for {config['stock_ticker']} not found. Train the model first.")
            else:
                agent = DQNAgent(11, 3)
                agent.model.load_state_dict(torch.load(model_path ))
                trader.add_strategy(DQNStrategy, {"model": agent})
        else:
            trader.add_strategy(config["selected_strategy"], params=config["strategy_params"])

        # Run the backtest
        try:
            # Execute the backtest
            metrics = trader.run(sigle_stock=1, stock_ticker=config["stock_ticker"])

            # Generate the performance chart
            chart = trader.plot()
            return metrics, chart
        except Exception as e:
            # Catch and display any errors during backtest execution
            st.error(f"Backtest failed: {e}")
            return None, None


    # Run both backtests
    metrics_1, chart_1 = run_backtest(config_1)
    metrics_2, chart_2 = run_backtest(config_2)

    # Display results
    col1, col2 = st.columns(2)

    if metrics_1 and chart_1 and metrics_2 and chart_2:
        col1, col2 = st.columns(2)
        with col1:
            st.write("### Configuration 1 Results")
            for metric, value in metrics_1.items():
                st.metric(label=metric, value=value)
            
        with col2:
            st.write("### Configuration 2 Results")
            for metric, value in metrics_2.items():
                st.metric(label=metric, value=value)

        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(chart_1)
        with col2:
            st.pyplot(chart_2)
        