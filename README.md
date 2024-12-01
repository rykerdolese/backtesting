# AI Trader Application

This project is an AI trading application that allows for backtesting different trading strategies. You can run the app locally or with Streamlit.

## Project Structure
- `app.py`: Main entry file for the Streamlit interface.
- `main.py`: Script for running the main application functionality.
- `backtrader`, `data`, `log`, `pages`, `trading`: Folders containing various modules, data, logs, pages, and trading strategies for the application.

## Installation and Requirements
Clone this repository and install the required dependencies:

###  For Mac<br>

- Run this first
```bash
brew install ta-lib
```
- Then
```bash
pip install -r requirements.txt
```
This project requires Python 3.11 or higher versions. Non ARM Macs will have to revise or manually install Torch and Tensorflow versions.

## Usage
###  Running the Application

- To run the main Python script:
```bash
python main.py
```
- To start the Streamlit app:
```bash
streamlit run app.py
```

## Features
- Provides several pre-built trading strategies like Buy and Hold, Moving Averages, Bollinger Bands, etc.

- Includes real-time stock data fetching and visualization.

- Allows backtesting of strategies with selectable date ranges, stocks, and other configurations.
