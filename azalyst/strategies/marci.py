import pandas as pd

from azalyst.config import BUY, SELL, HOLD


def signal(df: pd.DataFrame) -> int:
    if len(df) < 30:
        return HOLD

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # ── Global Armor Filter ──
    ema_200 = last.get("ema_200", last["close"])
    vol_ma = last.get("vol_ma_20", 0)
    high_conviction_vol = last["volume"] > vol_ma * 1.3 if vol_ma > 0 else True

    macd_accel_up = last["macd_hist_accel"] > 0 and last["macd_hist"] > 0
    adx_strong = last["adx"] >= 25 and last["adx"] > prev["adx"]
    atr_expanding = last["atr_14"] > last.get("atr_ma_20", 0)
    above_vwap = last["close"] > last.get("vwap", last["close"])
    ema_bullish = last["ema_20"] > last["ema_50"]

    if macd_accel_up and adx_strong and atr_expanding and above_vwap and ema_bullish:
        if last["close"] > ema_200 and high_conviction_vol:
            return BUY

    macd_accel_down = last["macd_hist_accel"] < 0 and last["macd_hist"] < 0
    below_vwap = last["close"] < last.get("vwap", last["close"])
    ema_bearish = last["ema_20"] < last["ema_50"]

    if macd_accel_down and adx_strong and atr_expanding and below_vwap and ema_bearish:
        if last["close"] < ema_200 and high_conviction_vol:
            return SELL

    return HOLD
