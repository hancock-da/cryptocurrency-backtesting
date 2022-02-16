# cryptocurrency-backtesting
*please note, these trading strategies are for educational purposes only and do not represent actual trading ideas*

1. crypto_snapshot.py pulls data for all USDT coin pairs from binance into a folder for backtesting.

2. strategies.py contains a number of strategies to backtest.
> * ADXStrategy
>> * Buy condition: OBV is greater than the 100 day OBV average, ADX greater than 25 and DI+ greater than DI- indicating a positive trend.
>> * Sell condition: If any of the following conditions are met OBV < 100 day OBV average, ADX < 25 or DI- < DI+

> * RSIStrategy
>> * Buy condition: RSI > 55 indicating a consistent uptrend. Can catch parabolic moves.
>> * Sell condition: RSI < 45 indicating the trend is down.

> * KCStrategy (TTM Squeeze)
>> * Buy condition: If Bollinger Bands are within Keltner Channels for at least 5 days and then break out indicating increased volatility.
>> * Sell condition: If the price closes below the Keltner Channel Midline (20 day EMA)

> * CandleStrategy
>> * Buy condition: If a three-line-strike candlestick pattern appears whilst in a downtrend (fast SMA < slow SMA) could indicate a reversal
>> * Sell condition: Stop-loss = buy price - 2(default) * ATR and Take-profit = Buy price + 2 * risk (buy price - stop-loss)
