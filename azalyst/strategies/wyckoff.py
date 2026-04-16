import pandas as pd

from azalyst.config import BUY, SELL, HOLD
from azalyst.candlestick import is_hammer, is_bullish_engulfing, is_bearish_engulfing, is_inverted_hammer

def signal(df: pd.DataFrame) -> int:
    if len(df) < 60:
        return HOLD

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # ── Global Armor Filter ──
    ema_200 = last.get("ema_200", last["close"])
    vol_ma = last.get("vol_ma_20", 0)

    # Look back over recent history to establish range (e.g. 50 candles)
    range_df = df.iloc[-60:-10]
    support = range_df["low"].min()
    resistance = range_df["high"].max()

    # Spring Event (Bullish) - Must occur above EMA 200 or as a major recovery
    # Price breaks down below support recently, then shoots back up
    recent_low = df["low"].tail(10).min()
    if recent_low < support:
        # We had a breakdown. Are we recovering?
        if last["close"] >= support and last["close"] > ema_200:
            # High-volume rejection is mandatory for institutional conviction
            if last["volume"] > vol_ma * 1.5:
                if is_hammer(last) or is_hammer(prev) or is_bullish_engulfing(last, prev):
                    return BUY

    # UTAD Event (Bearish)
    recent_high = df["high"].tail(10).max()
    if recent_high > resistance:
        if last["close"] <= resistance and last["close"] < ema_200:
            if last["volume"] > vol_ma * 1.5:
                if is_inverted_hammer(last) or is_inverted_hammer(prev) or is_bearish_engulfing(last, prev):
                    return SELL

    return HOLD
