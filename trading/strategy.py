from trading.base_strategy import *

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

## SMA (Naive and Cross SMA)
class NaiveMovingAverage(BaseStrategy):
    # Parameter for the moving average period
    params = dict(sma_period=30)  # Default period of 30 days

    def __init__(self):
        # Define the moving average indicator
        self.sma = bt.indicators.SMA(self.data.close, # Close price data
                                     period=self.params.sma_period)
        
        self.buy_signal = self.data.close > self.sma  # Price is above the SMA
        self.close_signal = self.data.close < self.sma # Price is below the SMA

    def next(self):
        # Check if we are already in a position
        if not self.position:
            # If not in a position, look for a BUY signal
            if self.buy_signal[0]: # 0 is the most recent signal
                self.buy()  # Enter a long position
        else:
            # If in a position, look for a close(sell) signal
            if self.close_signal[0]:  
                self.close()  # Exit the long position

class CrossMovingAverage(BaseStrategy):
     # Parameter for the moving average period
    params = dict(fast=5, slow=37)  # Default period of 5, 37 days
    def __init__(self):
        self.fast_sma = bt.indicators.SMA(
            self.data.close, 
            period=self.params.fast, 
            plotname="fast_day_sma"
        )

        self.slow_sma = bt.indicators.SMA(
            self.data.close, 
            period=self.params.slow, 
            plotname="slow_day_sma"
        )
        self.crossover = bt.indicators.CrossOver(self.fast_sma, self.slow_sma)
     
    def next(self):
        if self.position.size == 0:
            # fast_sma has crossed above slow_sma (buy)
            if self.crossover > 0:
                self.buy()

        if self.position.size > 0:
            # fast_sma has crossed below slow_sma (sell)
            if self.crossover < 0:
                self.close()

## Bollinger Bands
class BollingerBands(BaseStrategy):
    params = dict(period=20, devfactor=2)

    def __init__(self):
        self.bb = bt.indicators.BollingerBands(
            self.data, 
            period=self.params.period, 
            devfactor=self.params.devfactor
        )

    def next(self):
        signal_buy = self.data.close[0] < self.bb.lines.bot[0]
        signal_sell = self.data.close[0] > self.bb.lines.top[0]

        if self.position.size == 0:
            if signal_buy:
                self.buy()

        if self.position.size > 0:
            if signal_sell:
                self.close()

## Momentum
class Momentum(BaseStrategy):
    """
    https://en.wikipedia.org/wiki/Momentum_(technical_analysis)
    """

    params = dict(sma_period=50, momentum_period=14)

    def __init__(self):
        self.sma = bt.indicators.SMA(
            self.data.close, period=self.params.sma_period
        )
        self.momentum = bt.indicators.Momentum(
            self.data.close, period=self.params.momentum_period
        )
        self.buy_signal = self.momentum > 0
        self.close_signal = self.data.close < self.sma

    def next(self):
        if self.position.size == 0:
            if self.buy_signal[0]:
                self.buy()
        else:
            if self.close_signal[0]:
                self.close()

## RSI
class NaiveeRSI(BaseStrategy):
    """
    Buy when the RSI is below 30.
    Sells when the RSI is above 70.
    """
    # Set the default parameters for RSI
    params = dict(rsi_period=14, oversold=30, overbought=70)

    def __init__(self):
        # Define the RSI indicator
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period)

    def next(self):
        # Check if we are already in a position
        if not self.position:
            # If RSI is below the oversold threshold, it's a buy signal
            if self.rsi < self.params.oversold:
                self.buy()
        else:
            # If RSI is above the overbought threshold, it's a sell signal
            if self.rsi > self.params.overbought:
                self.close()

class RsiBollingerBands(BaseStrategy):
    """
    Buy when the RSI is below 30 and the price is below the lower Bollinger Band.
    Sell when the RSI is above 70 or the price is above the upper Bollinger Band.
    """

    params = dict(rsi_period=14, bb_period=20, bb_dev=2, oversold=30, overbought=70)

    def __init__(self):
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
        self.bbands = bt.indicators.BollingerBands(
            period=self.params.bb_period, devfactor=self.params.bb_dev
        )

    def next(self):
        buy_signal = (
            self.rsi < self.params.oversold
            and self.data.close[0] <= self.bbands.lines.bot[0]
        )
        close_signal = (
            self.rsi > self.params.overbought
            or self.data.close[0] >= self.bbands.lines.top[0]
        )

        if not self.position:
            if buy_signal:
                self.buy()
        else:
            if close_signal:
                self.close()

## ROC
class NaiveRateOfChange(BaseStrategy):
    """
    ROC = [(Current Close – Close n periods ago) / (Close n periods ago)]
    ROC is a momentum oscillator; other indicator types similar to ROC include MACD, RSI and ADX,
    https://www.avatrade.com/education/technical-analysis-indicators-strategies/roc-indicator-strategies

    """

    params = dict(period=20, threshold=0.08)

    def __init__(self):
        self.roc = bt.indicators.RateOfChange(self.data, period=self.params.period)
        self.buy_signal = self.roc > self.params.threshold
        self.close_signal = self.roc < -self.params.threshold

    def next(self):
        if not self.position:
            if self.buy_signal[0]:
                self.buy()

        if self.position.size > 0:
            if self.close_signal[0]:
                self.close()

class ROCMovingAverage(BaseStrategy):
    params = dict(roc_period=12, fast_ma_period=10, slow_ma_period=30)

    def __init__(self):
        self.roc = bt.indicators.RateOfChange(
            self.data.close, period=self.params.roc_period
        )
        self.fast_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.fast_ma_period
        )
        self.slow_ma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.slow_ma_period
        )
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        buy_signal = self.roc[0] > 0 and self.crossover[0] > 0
        close_signal = self.roc[0] < 0 or self.crossover[0] < 0

        if self.position.size == 0:
            if buy_signal:
                self.buy()

        if self.position.size > 0:
            if close_signal:
                self.close()


## Fear and Greed 
class FearGreed(BaseStrategy):
    def __init__(self):
        self.feargreed = self.datas[0].feargreed

    def next(self):
        if not self.position:
            if self.feargreed[0] < 20:
                self.buy()
        else:
            if self.feargreed[0] > 60:
                self.sell()

## Put Call
class PutCall(BaseStrategy):
    def __init__(self):
        self.putcall = self.datas[0].putcall

    def next(self):
        if self.putcall[0] > 1 and not self.position:
            self.buy()
        if self.putcall[0] < 0.45 and self.position.size > 0:
            self.sell()


## VIX
class VIX(BaseStrategy):
    def __init__(self):
        self.vix = self.datas[0].vix

    def next(self):
        if self.vix[0] > 35 and not self.position:
            self.buy()
        if self.vix[0] < 10 and self.position.size > 0:
            self.sell()