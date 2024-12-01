---

# Trading Strategies

This repository contains various trading strategies implemented using Backtrader, a Python library for backtesting. Strategies range from traditional technical analysis to AI-powered models. Each strategy is designed with specific objectives and methodologies, catering to different trading styles and periods.

---

## Single Stock Trading Strategies

### **1. Buy and Hold Strategy**
- **Objective**: Buy a stock once and hold it indefinitely without further trades.
- **Logic**:
  - If not in a position, initiate a buy order to go long.
  - Since there are no exit conditions, the position is held until the strategy ends.
- **Label**: Long-Term (5 years or more).

---

### **2. Naive Moving Average (SMA) Strategy**
- **Objective**: Use a simple moving average (SMA) to decide when to buy or sell.
- **Logic**:
  - Calculate the SMA over a specified period (default: 30 days).
  - **Buy Signal**: If the current price is above the SMA.
  - **Sell Signal**: If the current price falls below the SMA.
- **Label**: Medium-Term (3 months to 1 year).

---

### **3. Cross Moving Average Strategy**
- **Objective**: Use a crossover of two SMAs (fast and slow) to determine entry and exit points.
- **Logic**:
  - Calculate two SMAs: a fast SMA (shorter period) and a slow SMA (longer period).
  - **Buy Signal**: If the fast SMA crosses above the slow SMA.
  - **Sell Signal**: If the fast SMA crosses below the slow SMA.
- **Label**: Medium- to Long-Term (6 months to 2 years).

---

### **4. Bollinger Bands Strategy**
- **Objective**: Use Bollinger Bands to identify price breakouts and potential trend reversals.
- **Logic**:
  - Calculate the Bollinger Bands with a specified period and standard deviation factor.
  - **Buy Signal**: If the price drops below the lower band (potential oversold).
  - **Sell Signal**: If the price rises above the upper band (potential overbought).
- **Label**: Short- to Medium-Term (1 week to 6 months).

---

### **5. Momentum Strategy**
- **Objective**: Enter trades based on positive momentum and close them if momentum weakens or trends reverse.
- **Logic**:
  - Calculate a momentum indicator and SMA.
  - **Buy Signal**: If momentum is positive.
  - **Sell Signal**: If the price drops below the SMA.
- **Label**: Medium-Term (1 month to 1 year).

---

### **6. Naive RSI Strategy**
- **Objective**: Use the Relative Strength Index (RSI) to identify overbought or oversold conditions.
- **Logic**:
  - **Buy Signal**: If RSI < 30 (oversold).
  - **Sell Signal**: If RSI > 70 (overbought).
- **Label**: Short- to Medium-Term (1 week to 6 months).

---

### **7. RSI Bollinger Bands Strategy**
- **Objective**: Combine RSI and Bollinger Bands to filter entry and exit signals.
- **Logic**:
  - **Buy Signal**: RSI < 30 and price ≤ lower Bollinger Band.
  - **Sell Signal**: RSI > 70 or price ≥ upper Bollinger Band.
- **Label**: Short- to Medium-Term (2 weeks to 6 months).

---

### **8. Naive Rate of Change (ROC) Strategy**
- **Objective**: Use the Rate of Change (ROC) to capture momentum-based entry and exit points.
- **Logic**:
  - **Buy Signal**: If ROC > threshold (e.g., 0.08).
  - **Sell Signal**: If ROC < -threshold (e.g., -0.08).
- **Label**: Short-Term (2 weeks to 3 months).

---

### **9. ROC Moving Average Strategy**
- **Objective**: Combine the Rate of Change with a moving average crossover for trend-based entry and exit.
- **Logic**:
  - **Buy Signal**: ROC > 0 and fast SMA crosses above slow SMA.
  - **Sell Signal**: ROC < 0 or fast SMA crosses below slow SMA.
- **Label**: Medium-Term (1 to 3 months).

---

### **10. Fear and Greed Strategy**
- **Objective**: Trade based on the Fear and Greed Index.
- **Logic**:
  - **Buy Signal**: If the index < 30 (fear).
  - **Sell Signal**: If the index > 70 (greed).
- **Label**: Event-Driven.

---

### **11. Put/Call Ratio Strategy**
- **Objective**: Use the Put/Call ratio to determine market sentiment and trade accordingly.
- **Logic**:
  - **Buy Signal**: If Put/Call ratio > 1 (bearish sentiment).
  - **Sell Signal**: If Put/Call ratio < 0.45 (bullish sentiment reversal).
- **Label**: Event-Driven.

---

### **12. VIX Strategy**
- **Objective**: Trade based on volatility index (VIX) levels.
- **Logic**:
  - **Buy Signal**: If VIX > 35 (high fear in the market).
  - **Sell Signal**: If VIX < 10 (market stability).
- **Label**: Event-Driven.

---

## AI-Powered Strategies

### **13. Machine Learning (ML) Trading Strategy**
- **Objective**: Use machine learning models to predict buy/sell signals.
- **Logic**:
  - Train a model (e.g., Logistic Regression, Gradient Boosting) on historical data.
  - Generate buy/sell predictions based on indicators like SMA, Momentum, RSI, MACD, and Bollinger Bands.
  - **Buy Signal**: If the ML model predicts a positive trade outcome.
  - **Sell Signal**: If the ML model predicts a negative trade outcome.
- **Label**: Rolling (3 months to 1 year).

---

### **14. RNN Strategy**
- **Objective**: Use Recurrent Neural Networks (RNN) predictions for trading decisions.
- **Logic**:
  - Train an RNN model on historical prices.
  - **Buy Signal**: If predicted price > current price.
  - **Sell Signal**: If predicted price < current price.
- **Label**: Rolling (3 months to 1 year).

---

### **15. Reinforcement Learning (DQN) Strategy**
- **Objective**: Use Deep Q-Networks (DQN) to learn an optimal trading policy.
- **Logic**:
  - Train a DQN agent using an environment designed for stock trading.
  - The agent learns through exploration and rewards based on portfolio performance.
  - **Buy Signal**: Action output by the DQN agent suggests buying.
  - **Sell Signal**: Action output by the DQN agent suggests selling.
- **Label**: Rolling (6 months to 1 year).

---

## Strategy Summary Table

| Strategy Name                | Objective                        | Label                      | Typical Period Range       |
|------------------------------|----------------------------------|----------------------------|----------------------------|
| Buy and Hold                 | Hold long-term positions         | Long-Term                  | 5+ years                  |
| Naive Moving Average (SMA)   | Follow price-SMA trend           | Medium-Term                | 3 months to 1 year        |
| Cross Moving Average         | Use SMA crossovers              | Medium- to Long-Term       | 6 months to 2 years       |
| Bollinger Bands              | Identify price extremes          | Short- to Medium-Term      | 1 week to 6 months        |
| Momentum                     | Capture trend strength           | Medium-Term                | 1 month to 1 year         |
| Naive RSI                    | Identify overbought/oversold     | Short- to Medium-Term      | 1 week to 6 months        |
| RSI Bollinger Bands          | Combine RSI with Bollinger Bands | Short- to Medium-Term      | 2 weeks to 6 months       |
| Naive Rate of Change (ROC)   | Measure momentum                 | Short-Term                 | 2 weeks to 3 months       |
| ROC Moving Average           | Combine ROC with SMA crossover   | Medium-Term                | 1 to 3 months             |
| Fear and Greed               | Use Fear and Greed Index         | Event-Driven               | Targeted event periods    |
| Put/Call Ratio               | Measure sentiment through options| Event-Driven               | Targeted event periods    |
| VIX                          | Measure market volatility        | Event-Driven               | Targeted event periods    |
| Machine Learning (ML)        | Predict with ML models           | Rolling                    | 3 months to 1 year        |
| RNN                          | Predict with RNN models          | Rolling                    | 3 months to 1 year        |
| Reinforcement Learning (DQN) | Learn trading policy with DQN    | Rolling                    | 6 months to 1 year        |

--- 
