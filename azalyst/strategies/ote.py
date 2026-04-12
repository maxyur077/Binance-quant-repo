import pandas as pd

from azalyst.config import BUY, SELL, HOLD
from azalyst.candlestick import is_hammer, is_bullish_engulfing, is_bearish_engulfing, is_inverted_hammer

def signal(df: pd.DataFrame) -> int:
    if len(df) < 50:
        return HOLD

    last = df.iloc[-1]
    prev = df.iloc[-2]

    trend_lookback = df.tail(40)
    swing_high = trend_lookback["high"].max()
    swing_low = trend_lookback["low"].min()
    
    dealing_range = swing_high - swing_low
    if dealing_range <= 0:
        return HOLD

    # Fibonacci calculation
    fib_618 = swing_low + 0.618 * dealing_range
    fib_786 = swing_low + 0.786 * dealing_range
    
    # Are we in bullish OTE (retraced down from swing high)?
    # Assuming macro trend is up if recent price > EMA50
    if last["close"] > last["ema_50"]:
        if fib_618 <= last["low"] <= fib_786 or fib_618 <= last["close"] <= fib_786:
            if is_hammer(last) or is_bullish_engulfing(last, prev):
                if df["volume"].iloc[-1] > df["vol_ma_20"].iloc[-1]:
                    return BUY
                    
    # Are we in bearish OTE (retraced up from swing low)?
    fib_618_bear = swing_high - 0.618 * dealing_range
    fib_786_bear = swing_high - 0.786 * dealing_range

    if last["close"] < last["ema_50"]:
        if fib_786_bear <= last["high"] <= fib_618_bear or fib_786_bear <= last["close"] <= fib_618_bear:
            if is_inverted_hammer(last) or is_bearish_engulfing(last, prev):
                if df["volume"].iloc[-1] > df["vol_ma_20"].iloc[-1]:
                    return SELL

    return HOLD
