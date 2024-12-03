import streamlit as st
import numpy as np
import pandas as pd
import os
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from datetime import date


# dynamically load stock data
@st.cache_data
def load_stock_data(folder_path):
    '''
    loads csv stock data in a folder
    files to be loaded must be .csv and not start with the word "all"

    ex) "all_AAPL.csv" will not be read in, but "AAPL.csv" will. 

    returns stock data
    '''
    stock_data = {}
    for file in os.listdir(folder_path):
        if file.endswith(".csv") and not file.startswith("all"):
            ticker = file.split(".")[0]
            stock_data[ticker] = pd.read_csv(os.path.join(folder_path, file), index_col="Date", parse_dates=True)
    return stock_data

def filter_data_by_date(stock_data, start_date, end_date):
    '''
    Filters stock data based on the selected date range
    '''
    filtered_data = {}
    for ticker, data in stock_data.items():
        filtered_data[ticker] = data.loc[start_date:end_date]
    return filtered_data

def calculate_portfolio_metrics(stock_data):
    '''
    given data, return mean returns and covariances
    returns
        mean_returns
        cov_matrix
    '''
    price_data = pd.DataFrame({ticker: data['Close'] for ticker, data in stock_data.items()})
    returns = price_data.pct_change().dropna()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    return mean_returns, cov_matrix


def calculate_portfolio_metrics(stock_data):
    '''
    given data, return mean returns and covariances
    returns
        mean_returns
        cov_matrix
    '''
    price_data = pd.DataFrame({ticker: data['Close'] for ticker, data in stock_data.items()})
    returns = price_data.pct_change().dropna()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    return mean_returns, cov_matrix

def portfolio_performance(weights, mean_returns, cov_matrix):
    '''
    calculates weighted portfolio performance

    returns 
        portfolio_return
        portfolio_std
    '''
    portfolio_return = np.sum(mean_returns * weights) * 252
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    return portfolio_return, portfolio_std

def negative_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
    '''
    returns
        -sharpe_ratio
    '''
    p_return, p_std = portfolio_performance(weights, mean_returns, cov_matrix)
    sharpe_ratio = (p_return - risk_free_rate) / p_std
    return -sharpe_ratio

def optimize_portfolio(mean_returns, cov_matrix, risk_free_rate):
    '''
    Maximizes the sharpe ratio
    returns an array of optimal portfolio weights
    '''
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, risk_free_rate)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    result = minimize(
        negative_sharpe_ratio,
        num_assets * [1.0 / num_assets],
        args=args,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    return result.x


# Page configuration
st.set_page_config(page_title="Portfolio Optimization", 
                   page_icon="📌",
                   layout="wide")

# Streamlit app
st.title("Portfolio Optimization")
st.sidebar.header("Portfolio Inputs")

folder_path = "data/us_stock"
stock_data = load_stock_data(folder_path)
tickers = list(stock_data.keys())

# User picks their stocks
selected_tickers = st.sidebar.multiselect("Select Stocks", tickers, default=tickers[:3])

stock_start_date = pd.Timestamp('2014-01-02') ## probably shouldn't hard code this but this is true for our stock data
st.sidebar.header("Date Range")
start_date = st.sidebar.date_input("Start Date", value=pd.Timestamp("2020-01-01"), min_value=stock_start_date, max_value = pd.Timestamp(date.today()))
end_date = st.sidebar.date_input("End Date", value=pd.Timestamp("2023-01-01"), min_value=start_date, max_value = pd.Timestamp(date.today()))

if selected_tickers:
    selected_data = {ticker: stock_data[ticker] for ticker in selected_tickers}
    filtered_data = filter_data_by_date(selected_data, start_date, end_date)
    mean_returns, cov_matrix = calculate_portfolio_metrics(filtered_data)

    # user inputs the rf rate
    risk_free_rate = st.sidebar.number_input("Risk-Free Rate (%)", value=1.0, step=0.1) / 100

    # optimize portfolio
    optimal_weights = optimize_portfolio(mean_returns, cov_matrix, risk_free_rate)
    optimal_return, optimal_std = portfolio_performance(optimal_weights, mean_returns, cov_matrix)

    st.subheader("Optimal Portfolio Allocation")
    for ticker, weight in zip(selected_tickers, optimal_weights):
        st.write(f"{ticker}: {weight:.2%}")

    st.subheader("Portfolio Performance")
    st.write(f"Expected Annual Return: {optimal_return:.2%}")
    st.write(f"Annual Volatility: {optimal_std:.2%}")
    st.write(f"Sharpe Ratio: {(optimal_return - risk_free_rate) / optimal_std:.2f}")

    # plot efficient fronteir
    st.subheader("Efficient Frontier")
    frontier_returns = []
    frontier_volatilities = []


    simulation_size = 5000 # just for plotting

    for _ in range(simulation_size):
        weights = np.random.random(len(mean_returns))
        weights /= np.sum(weights)
        r, std = portfolio_performance(weights, mean_returns, cov_matrix)
        frontier_returns.append(r)
        frontier_volatilities.append(std)

    plt.figure(figsize=(10, 6))
    plt.scatter(frontier_volatilities, frontier_returns, 
                c=(np.array(frontier_returns) - risk_free_rate) / np.array(frontier_volatilities), cmap="viridis")
    plt.colorbar(label="Sharpe Ratio")
    plt.xlabel("Volatility")
    plt.ylabel("Return (%)")
    plt.scatter(optimal_std, optimal_return, color="red", label="Optimal Portfolio", marker="*")
    plt.legend()
    st.pyplot(plt)
