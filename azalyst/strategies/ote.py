import pandas as pd

from azalyst.config import BUY, SELL, HOLD
from azalyst.candlestick import is_hammer, is_bullish_engulfing, is_bearish_engulfing, is_inverted_hammer

def signal(df: pd.DataFrame) -> int:
    if len(df) < 50:
        return HOLD

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # ── Global Armor Filter ──
    ema_200 = last.get("ema_200", last["close"])
    vol_ma = last.get("vol_ma_20", 0)
    high_conviction_vol = last["volume"] > vol_ma * 1.2 if vol_ma > 0 else True

    # ── Dealing Range & Liquidity Sweep ──
    lookback_window = 40
    trend_lookback = df.tail(lookback_window)
    swing_high = trend_lookback["high"].max()
    swing_low = trend_lookback["low"].min()
    
    # Liquidity Sweep: Has price recently taken out stops?
    # For a LONG, we want to see price having dipped below a previous support.
    # We check if the low of any of the last 15 candles was lower than the swing_low of candles 15-40.
    prior_support = trend_lookback["low"].iloc[:-15].min()
    liquidity_swept_bull = any(trend_lookback["low"].iloc[-15:] < prior_support)
    
    prior_resistance = trend_lookback["high"].iloc[:-15].max()
    liquidity_swept_bear = any(trend_lookback["high"].iloc[-15:] > prior_resistance)

    dealing_range = swing_high - swing_low
    if dealing_range <= 0:
        return HOLD

    # Institutional "Golden Zone" (0.705 - 0.79)
    fib_ote_deep = swing_low + 0.705 * dealing_range
    fib_ote_max = swing_low + 0.79 * dealing_range
    
    # Bullish OTE setup
    if last["close"] > ema_200 and liquidity_swept_bull:
        if fib_ote_deep <= last["low"] <= fib_ote_max or fib_ote_deep <= last["close"] <= fib_ote_max:
            if is_hammer(last) or is_bullish_engulfing(last, prev):
                if high_conviction_vol:
                    return BUY
                    
    # Bearish OTE setup
    fib_ote_deep_bear = swing_high - 0.705 * dealing_range
    fib_ote_max_bear = swing_high - 0.79 * dealing_range

    if last["close"] < ema_200 and liquidity_swept_bear:
        if fib_ote_max_bear <= last["high"] <= fib_ote_deep_bear or fib_ote_max_bear <= last["close"] <= fib_ote_deep_bear:
            if is_inverted_hammer(last) or is_bearish_engulfing(last, prev):
                if high_conviction_vol:
                    return SELL

    return HOLD
