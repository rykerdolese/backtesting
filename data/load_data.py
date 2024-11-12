import os
import requests
import pandas as pd
import yfinance as yf
from tqdm import tqdm
from typing import List, Literal, Tuple
from datetime import datetime
from fake_useragent import UserAgent


class StockLoader(object):
    """
    A class to load stock data and save it as CSV files.
    """

    def __init__(
        self,
        stocks: List[str],
        market: Literal["us"] = "us",
        start_ym: Tuple[int, int] = (2024, 1),
        save_dir: str = "./data/us_stock/",
    ):
        self.stocks = stocks
        self.market = market
        self.start_ym = start_ym
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)

    def log(self, txt: str) -> None:
        print(txt)

    def save_one_stock_to_csv(self, stock_id: str) -> None:
        self.log(f"Working on: {stock_id}")
        try:
            if self.market == "us":
                start = f"{self.start_ym[0]:04d}-{self.start_ym[1]:02d}-01"
                print(start)
                df = yf.download(stock_id, start=start)
                df = df.reset_index()                
            else:
                raise ValueError("Market only supports 'us' ")

            filepath = os.path.join(self.save_dir, f"{stock_id}.csv")
            df.to_csv(filepath, index=False)
            self.log(f"Saved: {filepath}")
        except Exception as e:
            self.log(f"Error processing {stock_id}: {e}")


    def run(self) -> None:
        for stock_id in tqdm(self.stocks, desc="Loading stock data"):
            try:
                self.save_one_stock_to_csv(stock_id)
            except Exception as e:
                self.log(f"Error fetching data for {stock_id}: {e}")

        self.log("Finished all runs.")


def fetch_market_sentiment_data(start_date='2020-09-21', file_path = "./data/sentiment/"):
    """
    Fetches and combines Fear and Greed, put-call ratio, and VIX data from the API and local CSVs.
    """
    # Constants
    BASE_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/"
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    
    # Fetch Fear and Greed data from CNN's API
    response = requests.get(BASE_URL + start_date, headers=headers)
    data = response.json()
    
    # Load and prepare Fear and Greed data from CSV
    fng_data = pd.read_csv(file_path+'fear-greed.csv', usecols=['Date', 'Fear Greed'])
    fng_data['Date'] = pd.to_datetime(fng_data['Date'], format='%Y-%m-%d')
    fng_data.set_index('Date', inplace=True)
    fng_data.sort_index(inplace=True)
    
    # Load and prepare put-call ratio data from CSV
    putcall_data = pd.read_csv(file_path+'put-call.csv', usecols=['Date', 'Put Call'])
    putcall_data['Date'] = pd.to_datetime(putcall_data['Date'], format='%Y-%m-%d')
    putcall_data.set_index('Date', inplace=True)
    putcall_data.sort_index(inplace=True)
    
    # Load and prepare VIX data from CSV
    vix_data = pd.read_csv(file_path+'vix.csv', usecols=['Date', 'VIX'])
    vix_data['Date'] = pd.to_datetime(vix_data['Date'], format='%Y-%m-%d')
    vix_data.set_index('Date', inplace=True)
    vix_data.sort_index(inplace=True)
    
    # Update Fear and Greed data with the latest values from the API
    for entry in data.get('fear_and_greed_historical', {}).get('data', []):
        date = datetime.utcfromtimestamp(entry['x'] / 1000).strftime('%Y-%m-%d')
        fear_greed_value = int(entry['y'])
        fng_data.at[date, 'Fear Greed'] = fear_greed_value
    
    # Update put-call ratio data with the latest values if available
    if 'put_call_options' in data:
        for entry in data['put_call_options']['data']:
            date = datetime.utcfromtimestamp(entry['x'] / 1000).strftime('%Y-%m-%d')
            put_call_value = round(entry['y'], 2)
            putcall_data.at[date, 'Put Call'] = put_call_value
    
    # Update VIX data with the latest values if available
    if 'market_volatility_vix' in data:
        for entry in data['market_volatility_vix']['data']:
            date = datetime.utcfromtimestamp(entry['x'] / 1000).strftime('%Y-%m-%d')
            vix_value = entry['y']
            vix_data.at[date, 'VIX'] = vix_value
    
    # Combine the datasets, aligning on the Date index
    combined_data = pd.concat([fng_data, putcall_data, vix_data], axis=1)
    
    combined_data.to_csv(file_path+"sentiment.csv")
    return combined_data

if __name__ == "__main__":
    stock_loader = StockLoader(["AAPL", 
                          "MSFT",
                          "NVDA",
                          "GOOG",
                          "AMZN",
                          "META",
                          "BRK-B",
                          "LLY",
                          "AVGO",
                          "TSLA",
                          "WMT",
                          "JPM",
                          "V",
                          "UNH",
                          "XOM",
                          "ORCL",
                          "MA",
                          "HD",
                          "PG",
                          "COST",
                          "^SPX"], 
                          "us", (2014, 1), "./data/us_stock/")
    stock_loader.run()

    fetch_market_sentiment_data()
