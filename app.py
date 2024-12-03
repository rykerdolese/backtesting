import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd
from fredapi import Fred


# Helper functions

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
def plot_chart(stock_data, title, overall_market_condition):
    fig = px.line(stock_data, x=stock_data.index, y="Close", title=title)
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="Closing Price")
    if overall_market_condition == "Bullish":
        fig.update_traces(line_color="green")
    elif overall_market_condition == "Neutral":
        fig.update_traces(line_color="steelblue")
    else:
        fig.update_traces(line_color="red")
    st.plotly_chart(fig, use_container_width=True)
    st.write(stock_data.tail())  # Display the last few rows of data


def display_major_indices(metrics):
    columns = st.columns(len(metrics))  # Create one column per index
    
    for col, (index, data) in zip(columns, metrics.items()):
        if data["value"] is not None:
            col.metric(
                label=index,
                value=f"{data['value']:.2f}",
                delta=f"{data['delta']:.2f}%",
                delta_color="normal",  # Green for positive, red for negative
            )
        else:
            col.metric(label=index, value="Unavailable")

# Analyze and prepare data for major indices
def prepare_index_metrics(indices_data):
    metrics = {}
    for index_name, data in indices_data.items():
        if data is not None and not data.empty:
            try:
                # Calculate current value and percentage change
                current_value = data["Close"].iloc[-1]
                percentage_change = (data["Close"].iloc[-1] - data["Close"].iloc[-2]) / data["Close"].iloc[-2] * 100
                metrics[index_name] = {"value": current_value, "delta": percentage_change}
            except Exception:
                metrics[index_name] = {"value": None, "delta": None}
        else:
            metrics[index_name] = {"value": None, "delta": None}
    return metrics

# Helper function to plot data
def plot_indicator(df, title, y_label):
    fig = px.line(
        df,
        x=df.index,
        y=df.columns[0],
        title=title,
        labels={"value": y_label, "index": "Date"},
    )
    fig.update_layout(title_font_size=16, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

# Page configuration
st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide"
)

# Main content
st.write("# Welcome to QuantFIN! 👋")

# Sidebar options for selecting stock ticker, period, and interval
st.sidebar.markdown("## **Stock Data Settings**")
ticker_symbol = st.sidebar.selectbox(
    "Select Stock Ticker", 
    [
        "^GSPC", "^DJI", "^IXIC", # Major indices
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

# Default ticker settings for major indices
default_period = "1mo"
default_interval = "1d"

# Fetch real-time stock data for major indices
indices_data = {
    "S&P 500": fetch_realtime_stock_data("^GSPC", default_period, default_interval),
    "NASDAQ Composite": fetch_realtime_stock_data("^IXIC", default_period, default_interval),
    "Dow Jones Industrial": fetch_realtime_stock_data("^DJI", default_period, default_interval),
}

# Prepare metrics for display
metrics = prepare_index_metrics(indices_data)

# Fetch data for selected ticker
stock_data = fetch_realtime_stock_data(ticker_symbol, period, interval)

# Determine overall market condition
try:
    sp500_change = metrics["S&P 500"]["delta"]
    nasdaq_change = metrics["NASDAQ Composite"]["delta"]
    dow_change = metrics["Dow Jones Industrial"]["delta"]

    if sp500_change > 0 and nasdaq_change > 0 and dow_change > 0:
        overall_market_condition = "Bullish"
    elif sp500_change < 0 and nasdaq_change < 0 and dow_change < 0:
        overall_market_condition = "Bearish"
    else:
        overall_market_condition = "Neutral"
except KeyError:
    overall_market_condition = "Unavailable"

st.subheader(f"Overall Market Condition: {overall_market_condition}")
# Display the metrics in the sidebar
display_major_indices(metrics)

# Show the main ticker data chart
if stock_data is not None:
    st.subheader(f"{ticker_symbol} Stock Data")
    plot_chart(stock_data, f"{ticker_symbol} Closing Price", overall_market_condition)
else:
    st.warning("No data available for the selected ticker and parameters.")


# Initialize FRED API
fred = Fred(api_key='e6ffaec586eee5e9a907f15c1d38688e')

# Function to fetch economic indicator data
def fetch_economic_indicators():
    indicators = {}
    indicators["federal_fund_effective_rate"] = fred.get_series('FEDFUNDS')
    indicators["inflation_rate"] = fred.get_series('CORESTICKM159SFRBATL')
    indicators["gdp"] = fred.get_series('GDP')
    indicators["unemployment_rate"] = fred.get_series('UNRATE')
    indicators["consumer_sentiment"] = fred.get_series('UMCSENT')
    indicators["cli"] = fred.get_series('USALOLITONOSTSAM')
    indicators["yield_curve"] = fred.get_series('T10Y3MM')
    indicators["coincident"] = fred.get_series('BBKMCOIX')
    indicators["lagging"] = fred.get_series('M16005USM358SNBR')
    indicators["recession_indicator"] = fred.get_series('USREC')
    return indicators

# Function to convert series to DataFrame
def convert_to_dataframe(series, column_name):
    df = pd.DataFrame(series, columns=[column_name])
    return df

# Check if data is already loaded in session state
if "economic_indicators" not in st.session_state:
    st.session_state["economic_indicators"] = fetch_economic_indicators()

# Convert series to DataFrame
indicators = st.session_state["economic_indicators"]
federal_fund_effective_rate_df = convert_to_dataframe(indicators["federal_fund_effective_rate"], "Federal Fund Effective Rate")
inflation_rate_df = convert_to_dataframe(indicators["inflation_rate"], "Inflation Rate")
gdp_df = convert_to_dataframe(indicators["gdp"], "GDP")
unemployment_df = convert_to_dataframe(indicators["unemployment_rate"], "Unemployment Rate")
consumer_sentiment_df = convert_to_dataframe(indicators["consumer_sentiment"], "Consumer Sentiment")
cli_df = convert_to_dataframe(indicators["cli"], "Composite Leading Indicator")
yield_curve_df = convert_to_dataframe(indicators["yield_curve"], "Yield Curve: 10Y - 3M")
coincident_df = convert_to_dataframe(indicators["coincident"], "Coincident Indicators")
lagging_df = convert_to_dataframe(indicators["lagging"], "Lagging Indicators")
recession_indicator_df = convert_to_dataframe(indicators["recession_indicator"], "Recession Indicators")

# Helper function to fetch stock data
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

# Function to plot indicators
def plot_indicator(df, title, y_label):
    fig = px.line(
        df,
        x=df.index,
        y=df.columns[0],
        title=title,
        labels={"value": y_label, "index": "Date"},
    )
    fig.update_layout(title_font_size=16, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)


# Expandable Dashboard
with st.expander("📊 Economic Indicators Dashboard"):
    st.write("""
    This dashboard provides an overview of key economic indicators such as Federal Funds Rate, Inflation, GDP, 
    Unemployment, Consumer Sentiment, Yield Curve, and more. These indicators help assess the current state of 
    the economy and identify trends.
    """)

    # Monetary Policy Indicators
    st.header("Monetary Policy Indicators")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Federal Funds Effective Rate")
        plot_indicator(federal_fund_effective_rate_df, "Federal Funds Effective Rate", "Rate (%)")
        st.write(federal_fund_effective_rate_df.tail())
    with col2:
        st.subheader("Inflation Rate")
        plot_indicator(inflation_rate_df, "Inflation Rate", "Rate (%)")
        st.write(inflation_rate_df.tail())

    # Economic Growth Indicators
    st.header("Economic Growth Indicators")
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Gross Domestic Product (GDP)")
        plot_indicator(gdp_df, "GDP", "Value (in billions)")
        st.write(gdp_df.tail())
        
        st.subheader("Coincident Indicators")
        plot_indicator(coincident_df, "Coincident Indicators", "Index Value")
        st.write(coincident_df.tail())
    with col4:
        st.subheader("Yield Curve (10Y - 3M Spread)")
        plot_indicator(yield_curve_df, "Yield Curve Spread", "Spread (%)")
        st.write(yield_curve_df.tail())
        
        st.subheader("Lagging Indicators")
        plot_indicator(lagging_df, "Lagging Indicators", "Index Value")
        st.write(lagging_df.tail())

    # Employment and Consumer Sentiment
    st.header("Employment and Consumer Sentiment")
    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Unemployment Rate")
        plot_indicator(unemployment_df, "Unemployment Rate", "Rate (%)")
        st.write(unemployment_df.tail())
    with col6:
        st.subheader("Consumer Sentiment")
        plot_indicator(consumer_sentiment_df, "Consumer Sentiment", "Index Value")
        st.write(consumer_sentiment_df.tail())

    # Recession Indicators
    st.header("Recession Indicators")
    st.subheader("Recession Indicators")
    plot_indicator(recession_indicator_df, "Recession Indicators", "Value (0 = No Recession, 1 = Recession)")
    st.write(recession_indicator_df.tail())
