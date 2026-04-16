import pandas as pd

from azalyst.config import BUY, SELL, HOLD


def signal(df: pd.DataFrame) -> int:
    if len(df) < 55:
        return HOLD

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # ── Global Armor Filter ──
    ema_200 = last.get("ema_200", last["close"])
    vol_ma = last.get("vol_ma_20", 0)
    high_conviction_vol = last["volume"] > vol_ma * 1.3 if vol_ma > 0 else True

    # Bullish Trend: EMA 9 > 21 > 50 AND price above EMA 200
    bull_stack = (df["ema_9"] > df["ema_21"]).tail(5).all() and \
                 (df["ema_21"] > df["ema_50"]).tail(5).all()

    if bull_stack and last["close"] > ema_200:
        pullback_to_ema21 = abs(last["close"] - last["ema_21"]) <= 0.2 * last["atr_14"]
        bullish_conviction = last["close"] > last["open"] and (last["close"] - last["open"]) > 0.5 * (last["high"] - last["low"])
        supertrend_bull = last["supertrend_dir"] == 1
        
        if pullback_to_ema21 and bullish_conviction and supertrend_bull and high_conviction_vol:
            return BUY

    # Bearish Trend: EMA 9 < 21 < 50 AND price below EMA 200
    bear_stack = (df["ema_9"] < df["ema_21"]).tail(5).all() and \
                 (df["ema_21"] < df["ema_50"]).tail(5).all()

    if bear_stack and last["close"] < ema_200:
        bounce_to_ema21 = abs(last["close"] - last["ema_21"]) <= 0.2 * last["atr_14"]
        bearish_conviction = last["close"] < last["open"] and (last["open"] - last["close"]) > 0.5 * (last["high"] - last["low"])
        supertrend_bear = last["supertrend_dir"] == -1

        if bounce_to_ema21 and bearish_conviction and supertrend_bear and high_conviction_vol:
            return SELL

    return HOLD
