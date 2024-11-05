# Trading Strategies
## Single Stock Trading

### 1. **Buy and Hold Strategy**
- **Objective**: Buy a stock once and hold it indefinitely without further trades.
- **Logic**:
  - If not in a position, initiate a buy order to go long.
  - Since there are no exit conditions, the position is held until the strategy ends.
  
---

### 2. **Naive Moving Average (SMA) Strategy**
- **Objective**: Use a simple moving average (SMA) to decide when to buy or sell.
- **Logic**:
  - Calculate the SMA over a specified period (default 30 days).
  - Buy Signal: If the current price is above the SMA.
  - Sell Signal: If the current price falls below the SMA.
  - This strategy assumes that price crossing above the SMA indicates an uptrend and vice versa.

---

### 3. **Cross Moving Average Strategy**
- **Objective**: Use a crossover of two SMAs (fast and slow) to determine entry and exit points.
- **Logic**:
  - Calculate two SMAs: a fast SMA (shorter period) and a slow SMA (longer period).
  - Buy Signal: If the fast SMA crosses above the slow SMA.
  - Sell Signal: If the fast SMA crosses below the slow SMA.
  - The crossover is intended to capture trend shifts by using short-term movements (fast SMA) relative to long-term trends (slow SMA).

---

### 4. **Bollinger Bands Strategy**
- **Objective**: Use Bollinger Bands to identify price breakouts and potential trend reversals.
- **Logic**:
  - Calculate the Bollinger Bands with a specified period and standard deviation factor.
  - Buy Signal: If the price drops below the lower band (potential oversold).
  - Sell Signal: If the price rises above the upper band (potential overbought).
  - This strategy assumes that prices tend to revert to the mean, using bands to identify extremes.

---

### 5. **Momentum Strategy**
- **Objective**: Enter trades based on positive momentum and close them if momentum weakens or trends reverse.
- **Logic**:
  - Calculate SMA over a specified period to define the trend.
  - Calculate a momentum indicator for a specified period to assess momentum direction.
  - Buy Signal: If momentum is positive (indicating an upward trend).
  - Sell Signal: If the price drops below the SMA (indicating a trend reversal).
  - Momentum strategies typically bet that strong trends will continue.

---

### 6. **Naive RSI Strategy**
- **Objective**: Use the Relative Strength Index (RSI) to identify overbought or oversold conditions.
- **Logic**:
  - Calculate RSI for a given period (default 14 days).
  - Buy Signal: If RSI is below 30 (indicating oversold).
  - Sell Signal: If RSI is above 70 (indicating overbought).
  - This strategy takes a contrarian approach, expecting that overbought or oversold conditions will result in a reversal.

---

### 7. **RSI Bollinger Bands Strategy**
- **Objective**: Combine RSI and Bollinger Bands to filter entry and exit signals.
- **Logic**:
  - Calculate RSI and Bollinger Bands.
  - Buy Signal: If RSI is below 30 and the price is below the lower Bollinger Band.
  - Sell Signal: If RSI is above 70 or the price is above the upper Bollinger Band.
  - Combining RSI and Bollinger Bands adds an additional filter, aiming for high-probability trades.

---


### 8. **Naive Rate of Change (ROC) Strategy**
- **Objective**: Use the Rate of Change (ROC) to capture momentum-based entry and exit points.
- **Logic**:
  - Calculate the ROC over a specified period (default 20 days).
  - Buy Signal: If ROC is above a specified positive threshold (indicating upward momentum).
  - Sell Signal: If ROC is below a specified negative threshold (indicating downward momentum).
  - ROC measures momentum and identifies potential trend continuations or reversals.

---

### 9. **ROC Moving Average Strategy**
- **Objective**: Combine the Rate of Change with a moving average crossover for trend-based entry and exit.
- **Logic**:
  - Calculate the ROC, a fast SMA, and a slow SMA.
  - Buy Signal: If ROC is positive and the fast SMA crosses above the slow SMA.
  - Sell Signal: If ROC is negative or the fast SMA crosses below the slow SMA.
  - This strategy combines momentum (ROC) with moving average crossover to increase signal strength.

---