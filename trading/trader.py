
import glob
import os
import backtrader as bt
import pandas as pd
from typing import Optional, List
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from trading.utils import *
from trading.base_strategy import *
from trading.traditional_strategies import *
from trading.ai_strategies import *

class PandasData_Customized(bt.feeds.PandasData):
    lines = ('feargreed', 'putcall', 'vix', 'predictions')
    params = (('feargreed', -4),
              ('putcall', -3),
              ('vix', -2),
              ('predictions', -1),
              )  # Position of the 'fear_greed' column in df

class AITrader:
    """
    AITrader is a wrapper for Backtrader functions, designed to accelerate the strategy development process.
    """

    def __init__(
        self,
        strategy: Optional[BaseStrategy] = None,
        cash: int = 1000000, # starting cash balance
        commission: float = 0.001425, # Commission rate for trades
        start_date: str = None,
        end_date: str = None,
        data_dir: Optional[str] = "./data/us_stock/",
        log_file: str = "./log/trading_log.txt"
    ):
        """
        Initializes the AITrader with the given parameters.
        """
        self.cash = cash
        self.commission = commission
        self.start_date = start_date
        self.end_date = end_date
        self.strategy = strategy
        self.data_dir = data_dir
        self.log_file = log_file
        self.cerebro = bt.Cerebro() # backtrader engine

        # Open the log file in write mode and store the file handle
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        self.log_handle = open(self.log_file,"a")
        self.log("--- AITrader initialization ---")    

    def log(self, txt: str) -> None:
        """
        Logs a message to the console.
        """
        print(txt)
        self.log_handle.write(txt + '\n')
        self.log_handle.flush()  # Ensure the message is written to the file immediately

    def add_strategy(self, strategy: BaseStrategy, params: Optional[dict] = None, model=None) -> None:
        """
        Adds a trading strategy to the cerebro instance.
        """
        self.strategy = strategy
        if params:
            if model:
                self.cerebro.addstrategy(strategy, model=model, **params)
                self.log(f"Strategy '{strategy.__name__}' added with model and parameters: {params}")
            else:
                self.cerebro.addstrategy(strategy, **params)
                self.log(f"Strategy '{strategy.__name__}' added with parameters: {params}")
        else:
            if model:
                self.cerebro.addstrategy(strategy, model=model)
                self.log(f"Strategy '{strategy.__name__}' added with model.")
            else:
                self.cerebro.addstrategy(strategy)
                self.log(f"Strategy '{strategy.__name__}' added without parameters.")

    def add_one_stock(self, df: Optional[pd.DataFrame] = None) -> None:
        """
        Loads classic test data into the cerebro instance.
        """
        df = df[self.start_date : self.end_date]
        # feed = bt.feeds.PandasData(
        #     dataname=df,
        #     openinterest=None,
        #     timeframe=bt.TimeFrame.Days,
        # )
        feed = PandasData_Customized(
                dataname=df,
                openinterest=None,
                timeframe=bt.TimeFrame.Days,
            )
        self.cerebro.adddata(feed)
        self.log("Data loaded.")

    def add_stocks(self, date_col: str = "Date") -> None:
        """
        Loads portfolio data for multiple stocks into the cerebro instance.
        """
        files = glob.glob(os.path.join(self.data_dir, "*.csv"))
        print(files)
        for file in files:
            df = pd.read_csv(file, parse_dates=[date_col], index_col=[date_col])
            df = df[self.start_date : self.end_date]
            ticker = extract_ticker_from_path(file)
            # data = bt.feeds.PandasData(
            #     dataname=df, 
            #     name=ticker, 
            #     timeframe=bt.TimeFrame.Days, 
            #     plot=False
            # )
            # Initialize the custom data feed
            data = PandasData_Customized(
                dataname=df,
                name=ticker,
                timeframe=bt.TimeFrame.Days,
                plot=False
            )
            self.cerebro.adddata(data, name=ticker)
            self.log(f"Loaded data for ticker: {ticker}")

    def add_analyzers(self) -> None:
        """
        Adds analyzers to the cerebro instance.
        """
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="SharpeRatio")
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name="DrawDown")
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name="Returns")
        self.log("Analyzers added.")
        self.log("\n--- Backtesting ---")

    def add_broker(self) -> None:
        """
        Configures the broker settings.
        Sets the broker’s starting cash and commission rate.
        """
        self.cerebro.broker.setcash(self.cash)
        self.cerebro.broker.setcommission(commission=self.commission)
        self.log(f"Starting Value: {self.cerebro.broker.getvalue()}")

    def add_sizer(self) -> None:
        """
        Sets the sizer for position sizing.
        """
        self.cerebro.addsizer(bt.sizers.PercentSizer, percents=95)
        self.log("Sizer set to 95%.")

    def analyze(self, result: List[bt.Strategy]) -> dict:
        """
        Analyzes the results of the backtest and returns metrics for comparison.
        """
        metrics = {}
        self.log("\n---Result Analysis---")
        metrics["Ending Value"] = round(self.cerebro.broker.getvalue())
    
        # Extract performance metrics
        returns = result[0].analyzers.Returns.get_analysis() if hasattr(result[0].analyzers, "Returns") else None
        sharpe_ratio = result[0].analyzers.SharpeRatio.get_analysis().get("sharperatio") if hasattr(result[0].analyzers, "SharpeRatio") else None
        drawdown = result[0].analyzers.DrawDown.get_analysis() if hasattr(result[0].analyzers, "DrawDown") else None

        if returns:
            metrics["Total Returns (%)"] = round(returns.get("rtot", 0) * 100, 2)
            metrics["Annualized Returns (%)"] = round(returns.get("rnorm", 0) * 100, 2)

        if sharpe_ratio is not None:
            metrics["Sharpe Ratio"] = round(sharpe_ratio, 3)

        if drawdown:
            metrics["Max Drawdown (%)"] = round(drawdown.get("max", {}).get("drawdown", 0), 2)

        # Log the metrics
        for metric, value in metrics.items():
            self.log(f"{metric}: {value}")
        
        # Evaluate based on metrics
        self.log("\n--- Strategy Evaluation ---")
        if metrics["Total Returns (%)"] > 0:
            self.log("Total Returns are positive, indicating a profitable strategy.")
        elif metrics["Total Returns (%)"] < 0:
            self.log("Total Returns are negative, indicating a loss.")
        else:
            self.log("No Returns.")

        if sharpe_ratio:
            if metrics["Sharpe Ratio"] > 1:
                self.log("Good risk-adjusted returns (Sharpe Ratio > 1), indicating a potentially effective strategy.")
            elif metrics["Sharpe Ratio"] > 2:
                self.log("Excellent risk-adjusted returns (Sharpe Ratio > 2).")
            else:
                self.log("Low risk-adjusted returns, suggesting that risk might not be well compensated.")

        if drawdown and metrics["Max Drawdown (%)"] > 20:
            self.log("High maximum drawdown (> 20%), which may indicate high risk.")
        else:
            self.log("Max Drawdown is within acceptable limits (< 20%), suggesting a stable strategy.")
        return metrics
    def run(self, sigle_stock=1, stock_ticker="AAPL") -> None:
        """
        Runs the backtest with the specified data type and sizer.
        """
        if self.strategy:
            if self.strategy != RNNStrategy:
                if sigle_stock == 1:
                    data = pd.read_csv(self.data_dir + f"all_{stock_ticker}.csv", 
                                    parse_dates=["Date"], 
                                    index_col="Date")
                    self.add_one_stock(data) 
                else:
                    self.add_stocks()
            else:
                if sigle_stock == 1:
                    data = pd.read_csv(self.data_dir + f"predictions/{stock_ticker}.csv", 
                                    parse_dates=["Date"], 
                                    index_col="Date")
                    self.add_one_stock(data) 
                else:
                    self.add_stocks()
            self.add_broker()
            self.add_sizer()
            self.add_analyzers()
            result = self.cerebro.run()
            analysis = self.analyze(result)
        else:
            raise ValueError("No strategy specified.")
        return analysis

    def plot(self) -> None:
        """
        Plots the results of the backtest.
        """
        # self.cerebro.plot()
        figs = self.cerebro.plot(iplot=False)
        figure = figs[0][0]  # Access the first figure from the nested list
        return figure
    
    def __del__(self):
        """
        Ensures the log file is closed when the instance is destroyed.
        """
        self.log_handle.close()

    
    def capture_backtest_data(self) -> dict:
        """
        Runs the backtest and captures data, indicators, portfolio values, cash balance,
        and buy/sell signals for each stock.
        """
        captured_data = {
            'portfolio_value': [],
            'cash': [],
            'buy_signals': [],
            'sell_signals': [],
            'ohlc_data': []
        }

        # Run the backtest
        result = self.cerebro.run()

        # Capture OHLC data for each stock
        for data in self.cerebro.datas:
            ohlc_data = pd.DataFrame({
                'Date': data.datetime.array,
                'Open': data.open.array,
                'High': data.high.array,
                'Low': data.low.array,
                'Close': data.close.array,
                'Volume': data.volume.array,
            })
            ohlc_data['Date'] = pd.to_datetime(ohlc_data['Date'], unit='s')
            captured_data['ohlc_data'].append({'ticker': data._name, 'data': ohlc_data})

        # Capture portfolio values and cash balance at each step
        for i in range(len(self.cerebro.datas[0].datetime.array)):
            captured_data['portfolio_value'].append(self.cerebro.broker.getvalue())
            captured_data['cash'].append(self.cerebro.broker.getcash())

        print(captured_data["buy_signals"])
        return captured_data
