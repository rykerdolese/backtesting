import streamlit as st
import yfinance as yf
import streamlit as st
import plotly.express as px

## helper functions

# Function to fetch stock data
def fetch_realtime_stock_data(ticker_symbol, period, interval):
    try:
        stock_data = yf.download(ticker_symbol, period=period, interval=interval)
    except Exception as e:
        if "15m data not available" in str(e):
            st.warning(f"15-minute data not available for the specified period. Fetching hourly data instead.")
            stock_data = yf.download(ticker_symbol, period=period, interval="1h")
        else:
            st.error(f"Error fetching data for {ticker_symbol}: {e}")
            return None
    return stock_data

# Function to plot charts
def plot_chart(stock_data, title, overall_market_condition ):
    fig = px.line(stock_data, x=stock_data.index, y="Close", title=title)
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="Closing Price")
    if overall_market_condition == "Bullish":
        fig.update_traces(line_color="green")
    elif overall_market_condition == 'Nuetral':
        fig.update_traces(line_color="steelblue")
    else:
        fig.update_traces(line_color="red")
    st.plotly_chart(fig, use_container_width=True)
    st.write(stock_data.tail())  # Display the last few rows of data

# page config
st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)

# content only for Home page
st.write("# Welcome to QuantFIN! 👋")

# Sidebar options for selecting stock ticker, period, and interval
st.sidebar.markdown("## **Stock Data Settings**")
ticker_symbol = st.sidebar.selectbox(
    "Select Stock Ticker", 
    [
        "^GSPC", "^DJI", "^IXIC",  # Major US indices
        "AAPL", "MSFT", "NVDA", "GOOG", "AMZN", "META", "BRK-B", "LLY", 
        "AVGO", "TSLA", "WMT", "JPM", "V", "UNH", "XOM", "ORCL", "MA", "HD", "PG", "COST"
    ]
)

allowed_intervals = {
    "1d": ["1m", "5m", "15m", "1h"],
    "5d": ["5m", "15m", "1h", "1d"],
    "1mo": ["15m", "1h", "1d", "1wk"],
    "3mo": ["1h", "1d", "1wk"],
    "6mo": ["1h", "1d", "1wk"],
    "1y": ["1d", "1wk", "1mo"],
    "2y": ["1d", "1wk", "1mo"],
    "5y": ["1wk", "1mo"],
    "10y": ["1mo"],
    "ytd": ["1d", "1wk"],
    "max": ["1wk", "1mo"]
}
# Select period
period = st.sidebar.selectbox("Select Period", list(allowed_intervals.keys()), index=0)

# Dynamically change intervals based on period
valid_intervals = allowed_intervals[period]
interval = st.sidebar.selectbox("Select Interval", valid_intervals, index=0)


# Default ticker settings for S&P 500, Dow Jones, and NASDAQ (for market condition analysis)
default_period = "1d"
default_interval = "1m"

# Fetch data for selected ticker
stock_data = fetch_realtime_stock_data(ticker_symbol, period, interval)

# Fetch real-time stock data for S&P 500, Dow Jones, and NASDAQ to determine market condition
sp500_data = fetch_realtime_stock_data("^GSPC", default_period, default_interval)
dow_data = fetch_realtime_stock_data("^DJI", default_period, default_interval)
nasdaq_data = fetch_realtime_stock_data("^IXIC", default_period, default_interval)

try:
    sp500_percentage_change = (sp500_data['Close'].iloc[-1] - sp500_data['Close'].iloc[0]) / sp500_data['Close'].iloc[0] * 100
    dow_percentage_change = (dow_data['Close'].iloc[-1] - dow_data['Close'].iloc[0]) / dow_data['Close'].iloc[0] * 100
    nasdaq_percentage_change = (nasdaq_data['Close'].iloc[-1] - nasdaq_data['Close'].iloc[0]) / nasdaq_data['Close'].iloc[0] * 100
    if sp500_percentage_change > 0 and dow_percentage_change > 0 and nasdaq_percentage_change > 0:
        overall_market_condition = "Bullish"
    elif sp500_percentage_change < 0 and dow_percentage_change < 0 and nasdaq_percentage_change < 0:
        overall_market_condition = "Bearish"
    else :
        overall_market_condition = "Nuetral"
except BaseException as e:
    # An exception here probably means that some data is unnavailable
    overall_market_condition = "Unavailable"


st.subheader(f"Overall Market Condition: {overall_market_condition}")

# Show the main ticker data chart
if stock_data is not None:
    st.subheader(f"{ticker_symbol} Stock Data")
    plot_chart(stock_data, f"{ticker_symbol} Closing Price", overall_market_condition)
else:
    st.warning("No data available for the selected ticker and parameters.")
