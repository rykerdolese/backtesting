from tqdm import tqdm
import os
import pandas as pd
import yfinance as yf
from typing import List, Literal, Tuple


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

if __name__ == "__main__":
    loader = StockLoader(["AAPL", 
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
    loader.run()