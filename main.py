from trading.strategy import *
from trading.trader import *

if __name__ == "__main__":
    # Initialize the AITrader
    trader = AITrader(start_date="2023-01-01", end_date="2024-11-11")

    # Set your desired strategy; for example, using the BuyHoldStrategy
    trader.add_strategy(VIX)

    # Run the backtest
    trader.run(1, stock_ticker="TSLA")

    # Plot the results
    # trader.plot()