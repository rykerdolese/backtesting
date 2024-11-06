import streamlit as st
from datetime import datetime


# page config
st.set_page_config(
    page_title="Model",
    page_icon="💡",
)

# content only for backtesting page
# Title of the page
st.title("AI model training Page")


# Define list of stock tickers
available_stocks = [
    "AAPL", "MSFT", "NVDA", "GOOG", "AMZN", "META",
    "BRK-B", "LLY", "AVGO", "TSLA", "WMT", "JPM", 
    "V", "UNH", "XOM", "ORCL", "MA", "HD", "PG", 
    "COST", "^SPX"
]
# Dropdown menu for selecting a stock ticker
stock_ticker = st.selectbox("Select Training Stock Data", available_stocks)

# Define the minimum and maximum date range for backtesting
min_date = datetime(2014, 1, 1)
max_date = datetime(2024, 10, 31)

# Date inputs with limited range
start_date = st.date_input("Traning Data Start Date", datetime(2024, 1, 1), min_value=min_date, max_value=max_date)
end_date = st.date_input("Traning Data End Date", datetime(2024, 10, 1), min_value=min_date, max_value=max_date)

# Selected which model we want to train
available_models = ["Logistic regression", "Gradient boosting"]
model = st.selectbox("Select Training Stock Data", available_models)

# Button to start the training
if st.button("Start training"):
    pass