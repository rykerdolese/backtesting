import backtrader as bt


# Define the log file path

class BaseStrategy(bt.Strategy):
    """
    This class logs events such as orders and trades .
    It's the foundation for building custom trading strategies.
    """

    def log(self, txt, dt=None):
        """
        Log the provided text with a timestamp.
        """
        dt = dt or self.datas[0].datetime.date(0)
        log_message = f"{dt.isoformat()}, {txt}"
        print(log_message)

        # write into log file
        file = open("./log/trading_log.txt", "a") # log file
        file.write(log_message + '\n')
        file.flush()
    
    def notify_order(self, order):
        """
        Handle order notifications.
        Monitors the status of an order as it progresses 
        through different states (e.g., Submitted, Completed, Rejected).
        """
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # When an order completes, it logs the order type (BUY or SELL), 
        # the execution price, total cost, and commission.
        if order.status == order.Completed:
            if order.isbuy():
                self.log(
                    f"[BUY] EXECUTED at Price: {order.executed.price:<10.2f} | "
                    f"Total Cost: {order.executed.value:<10.2f} | "
                    f"Commision: {order.executed.comm:<10.2f}"
                )
            elif order.issell():
                self.log(
                    f"[SELL] EXECUTED at Price: {order.executed.price:<10.2f} | "
                    f"Total Cost: {order.executed.value:<10.2f} | "
                    f"Commision: {order.executed.comm:<10.2f}"
                )
            self.bar_executed = len(self)

        # If the order is canceled, rejected, or lacks margin, 
        # it logs the reason for the failure and resets self.order to None.
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            status_map = {
                order.Canceled: "Canceled",
                order.Margin: "Margin",
                order.Rejected: "Rejected",
                order.Partial: "Partial",
            }
            status = status_map.get(order.status, "Unknown")
            self.log(f"[{order.data._name}] Order placement failed - status: {status}")

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        """
        Handle trade notifications.
        Logs the gross and net profit for each completed trade.
        """
        if not trade.isclosed:
            return

        self.log(
            f"[OPERATION PROFIT] Gross: {trade.pnl:<10.2f} | "
            f"Net: {trade.pnlcomm:<10.2f}"
        )