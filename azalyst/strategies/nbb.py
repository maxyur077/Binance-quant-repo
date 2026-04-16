import pandas as pd

from azalyst.config import BUY, SELL, HOLD


def signal(df: pd.DataFrame) -> int:
    if len(df) < 25:
        return HOLD

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # ── Global Armor Filter ──
    ema_200 = last.get("ema_200", last["close"])
    vol_ma = last.get("vol_ma_20", 0)
    high_conviction_vol = last["volume"] > vol_ma * 1.5 if vol_ma > 0 else True

    bullish_engulfing = (last["close"] > last["open"]) and \
                        (prev["close"] < prev["open"]) and \
                        (last["close"] > prev["open"]) and \
                        (last["open"] < prev["close"])

    body_size = abs(last["close"] - last["open"])
    lower_wick = min(last["close"], last["open"]) - last["low"]
    is_hammer = lower_wick > 2 * body_size and last["close"] > last["open"]

    if bullish_engulfing or is_hammer:
        # Longs only above EMA 200
        if last["close"] > ema_200 and high_conviction_vol:
            return BUY

    bearish_engulfing = (last["close"] < last["open"]) and \
                        (prev["close"] > prev["open"]) and \
                        (last["close"] < prev["open"]) and \
                        (last["open"] > prev["close"])

    upper_wick = last["high"] - max(last["close"], last["open"])
    is_inv_hammer = upper_wick > 2 * body_size and last["close"] < last["open"]

    if bearish_engulfing or is_inv_hammer:
        # Shorts only below EMA 200
        if last["close"] < ema_200 and high_conviction_vol:
            return SELL

    return HOLD
