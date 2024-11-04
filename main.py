from strategy import *
from trader import *

if __name__ == "__main__":
    # Initialize the AITrader with default settings
    trader = AITrader()

    # Set your desired strategy; for example, using the BuyHoldStrategy
    trader.add_strategy(NaiveMovingAverage)

    # Run the backtest
    trader.run(1, stock_ticker="AAPL")

    # # Plot the results
    # trader.plot()