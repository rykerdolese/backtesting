from base_strategy import *

## BuyHold
class BuyHold(BaseStrategy):
    """
    Long-only strategy
    Buy a stock once and hold it indefinitely
    """
    def next(self):
        # Check if we are already in a position
        if not self.position:
            self.buy()