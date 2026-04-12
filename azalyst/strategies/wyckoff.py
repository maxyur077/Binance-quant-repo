import pandas as pd

from azalyst.config import BUY, SELL, HOLD
from azalyst.candlestick import is_hammer, is_bullish_engulfing, is_bearish_engulfing, is_inverted_hammer

def signal(df: pd.DataFrame) -> int:
    if len(df) < 60:
        return HOLD

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Look back over recent history to establish range (e.g. 50 candles)
    range_df = df.iloc[-60:-10]
    support = range_df["low"].min()
    resistance = range_df["high"].max()

    # Calculate time in range (naive check)
    # Are we roughly in a range? (resistance - support) shouldn't be too large
    range_size = resistance - support
    if range_size > 3 * last["atr_14"]: # 3 ATR is a decent sized range
        pass # Not invalidating, just a sanity check

    # Spring Event (Bullish)
    # Price breaks down below support recently, then shoots back up
    recent_low = df["low"].tail(10).min()
    if recent_low < support:
        # We had a breakdown. Are we recovering?
        if last["close"] >= support and last["close"] > last["open"]:
            # Recovered support. Good volume?
            if df["volume"].iloc[-1] > 1.2 * df["vol_ma_20"].iloc[-1] or df["volume"].iloc[-2] > 1.2 * df["vol_ma_20"].iloc[-2]:
                if is_hammer(last) or is_hammer(prev) or is_bullish_engulfing(last, prev):
                    return BUY

    # UTAD Event (Bearish)
    recent_high = df["high"].tail(10).max()
    if recent_high > resistance:
        if last["close"] <= resistance and last["close"] < last["open"]:
            if df["volume"].iloc[-1] > 1.2 * df["vol_ma_20"].iloc[-1] or df["volume"].iloc[-2] > 1.2 * df["vol_ma_20"].iloc[-2]:
                if is_inverted_hammer(last) or is_inverted_hammer(prev) or is_bearish_engulfing(last, prev):
                    return SELL

    return HOLD
