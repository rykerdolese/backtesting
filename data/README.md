
# Load Data Script

This repository includes data loading and processing scripts for financial analysis, specifically for backtesting trading strategies. 
## Files and Folders

- **data/sentiment/**: Contains sentiment data.
- **data/us_stock/**: Contains stock data and combine data.
- **load_data.py**: The main script to fetch, process data.
- **combine_data.py**: The script to combine data.


## Data Sources

1. **Stock Data**: Stock data is fetched using the `yfinance` library, which provides historical data for various tickers.
2. **Sentiment Data**: Sentiment data is sourced from CNN's Fear & Greed Index, available [here](https://www.cnn.com/markets/fear-and-greed). For the api: [api_link](https://production.dataviz.cnn.io/index/fearandgreed/graphdata).

## Usage


1. Run `load_data.py`:
   ```bash
   python load_data.py
   ```

   The script will:
   - Fetch stock data from Yahoo Finance for specified tickers.
   - Fetch sentiment data from CNN.


2. Run `load_data.py`:
   ```bash
   python combine_data.py
   ```

   The script will:
   - Combine the stock data and sentiment data for each ticker in the format `all_{stockticker}`.

## Output

The script will output combined data files labeled as `all_{stockticker}`, where `{stockticker}` is the stock ticker symbol. These files will contain both stock and sentiment data for each respective ticker, organized for easy access and analysis.

---
