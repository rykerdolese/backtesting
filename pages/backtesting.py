import streamlit as st
from datetime import datetime
from trading.trader import AITrader
from trading.base_strategy import *
from trading.strategy import (
    BuyHold, NaiveMovingAverage, CrossMovingAverage,
    BollingerBands, Momentum, NaiveeRSI,
    RsiBollingerBands, NaiveRateOfChange, ROCMovingAverage,
    FearGreed, PutCall, VIX
)
import mpld3
import streamlit.components.v1 as components

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

# Define available strategies and their default parameters
strategies = {
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
}

# Sidebar for selecting the strategy and other parameters
selected_strategy_name = st.sidebar.selectbox("Choose Strategy", list(strategies.keys()))
selected_strategy, default_params = strategies[selected_strategy_name]

# Sidebar inputs for the selected strategy's parameters
strategy_params = {}
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

# Define the minimum and maximum date range for backtesting
min_date = datetime(2014, 1, 1)
max_date = datetime(2024, 10, 31)

# Date inputs with limited range
start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1), min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", datetime(2024, 10, 1), min_value=min_date, max_value=max_date)

# Define list of stock tickers
available_stocks = [
    "AAPL", "MSFT", "NVDA", "GOOG", "AMZN", "META",
    "BRK-B", "LLY", "AVGO", "TSLA", "WMT", "JPM", 
    "V", "UNH", "XOM", "ORCL", "MA", "HD", "PG", 
    "COST", "^SPX"
]

# Dropdown menu for selecting a stock ticker
stock_ticker = st.sidebar.selectbox("Select Stock Ticker", available_stocks)

# Checkbox to choose between single stock or multiple stocks
single_stock = st.sidebar.checkbox("Single Stock", value=True)

# Button to start the backtest
if st.sidebar.button("Run Backtest"):
    

    # Initialize the AITrader with the selected dates
    trader = AITrader(start_date=start_date, end_date=end_date)
    
    # Run the backtest and capture logs in the file
    try:
        trader.add_strategy(selected_strategy, strategy_params)
        trader.run(1 if single_stock else 0, stock_ticker=stock_ticker)
    except ValueError as e:
        st.error(str(e))

    # Display log contents in Streamlit
    st.write("### Backtest Results")
    
    # open the log file path
    log_file_path = "./log/trading_log.txt"
    with open(log_file_path, "r") as file:
        log_content = file.read()
    
    st.text_area("Log File Content", log_content, height=400)
    
    # Display the backtest plot
    st.write("### Backtest Plot")
    st.pyplot(trader.plot())


        # fig_html = mpld3.fig_to_html(trader.plot())
        # components.html(fig_html)

    