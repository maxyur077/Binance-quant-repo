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
    high_volume_rejection = last["volume"] > vol_ma * 2.0 if vol_ma > 0 else True

    # ── Liquidity Sweep Detection ──
    prior_low = df["low"].iloc[-41:-1].min()
    sweep_low = last["low"] < prior_low and last["close"] > prior_low

    bullish_engulfing = last["close"] > last["open"] and \
                        prev["close"] < prev["open"] and \
                        last["close"] > prev["open"]

    pin_bar_low = (min(last["close"], last["open"]) - last["low"]) > \
                  2 * abs(last["close"] - last["open"])

    if sweep_low and last["close"] > ema_200:
        if (bullish_engulfing or pin_bar_low) and high_volume_rejection:
            if 40 <= last["rsi_14"] <= 70:
                return BUY

    prior_high = df["high"].iloc[-41:-1].max()
    sweep_high = last["high"] > prior_high and last["close"] < prior_high

    bearish_engulfing = last["close"] < last["open"] and \
                        prev["close"] > prev["open"] and \
                        last["close"] < prev["open"]

    pin_bar_high = (last["high"] - max(last["close"], last["open"])) > \
                   2 * abs(last["close"] - last["open"])

    if sweep_high and last["close"] < ema_200:
        if (bearish_engulfing or pin_bar_high) and high_volume_rejection:
            if 30 <= last["rsi_14"] <= 60:
                return SELL

    return HOLD
