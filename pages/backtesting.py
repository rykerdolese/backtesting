import streamlit as st
from datetime import datetime
from trading.trader import AITrader
from trading.base_strategy import *
from trading.strategy import (
    BuyHold, NaiveMovingAverage, CrossMovingAverage,
    BollingerBands, Momentum, NaiveeRSI,
    RsiBollingerBands, NaiveRateOfChange, ROCMovingAverage
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

# Sidebar for AI Trader Configuration
st.sidebar.title("AI Trader Configuration")

# Define available strategies in a dictionary for easy selection
strategies = {
    "Buy and Hold": BuyHold,
    "Naive Moving Average": NaiveMovingAverage,
    "Cross Moving Average": CrossMovingAverage,
    "Bollinger Bands": BollingerBands,
    "Momentum": Momentum,
    "Naive RSI": NaiveeRSI,
    "RSI with Bollinger Bands": RsiBollingerBands,
    "Naive Rate of Change (ROC)": NaiveRateOfChange,
    "ROC with Moving Average": ROCMovingAverage,
}

# Sidebar for selecting the strategy and other parameters
selected_strategy = st.sidebar.selectbox("Choose Strategy", list(strategies.keys()))

# Define the minimum and maximum date range for backtesting
min_date = datetime(2014, 1, 1)
max_date = datetime(2024, 10, 31)

# Date inputs with limited range
start_date = st.sidebar.date_input("Start Date", datetime(2020, 1, 1), min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", datetime(2021, 1, 1), min_value=min_date, max_value=max_date)

# Define list of stock tickers
available_stocks = [
    "AAPL", "MSFT", "NVDA", "GOOG", "AMZN", "META",
    "BRK-B", "LLY", "AVGO", "TSLA", "WMT", "JPM", 
    "V", "UNH", "XOM", "ORCL", "MA", "HD", "PG", 
    "COST", "SPX"
]

# Dropdown menu for selecting a stock ticker
stock_ticker = st.sidebar.selectbox("Select Stock Ticker", available_stocks)

# Checkbox to choose between single stock or multiple stocks
single_stock = st.sidebar.checkbox("Single Stock", value=True)

# Button to start the backtest
if st.sidebar.button("Run Backtest"):
    # Define the log file path
    log_file_path = "backtest_log.txt"

    # Initialize the AITrader with the selected dates
    trader = AITrader(start_date=start_date, end_date=end_date)
    
    # Run the backtest and capture logs in the file
    try:
        trader.add_strategy(strategies.get(selected_strategy))
        trader.run(1 if single_stock else 0, stock_ticker=stock_ticker)
    except ValueError as e:
        st.error(str(e))

    # Display log contents in Streamlit
    st.write("### Backtest Results")
    log_file_path = "trading_log.txt"
    with open(log_file_path, "r") as file:
        log_content = file.read()
    
    st.text_area("Log File Content", log_content, height=400)
    
    # Display the backtest plot
    st.write("### Backtest Plot")
    st.pyplot(trader.plot())


        # fig_html = mpld3.fig_to_html(trader.plot())
        # components.html(fig_html)

    