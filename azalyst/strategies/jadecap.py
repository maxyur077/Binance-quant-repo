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

    # Check for Liquidity Sweeps (must be high volume)
    # Uses 20-period lookback to find 'Stop Runs'
    recent_lows = df["low"].iloc[-21:-1].min()
    recent_highs = df["high"].iloc[-21:-1].max()

    sweep_low = last["low"] < recent_lows and last["close"] > recent_lows and last["volume"] > vol_ma * 1.5
    sweep_high = last["high"] > recent_highs and last["close"] < recent_highs and last["volume"] > vol_ma * 1.5

    # Break of Structure (BOS)
    bos_bullish = last["close"] > df["swing_high"].tail(10).min()
    bos_bearish = last["close"] < df["swing_low"].tail(10).max()

    # TRIPLE LOCK: BOTH Sweep AND BOS must be present
    if sweep_low and bos_bullish:
        if last["close"] > ema_200:
            rsi_ok = 40 <= last["rsi_14"] <= 70
            atr_expanding = last["atr_14"] > last.get("atr_ma_20", 0)
            if rsi_ok and atr_expanding:
                return BUY

    if sweep_high and bos_bearish:
        if last["close"] < ema_200:
            rsi_ok = 30 <= last["rsi_14"] <= 60
            atr_expanding = last["atr_14"] > last.get("atr_ma_20", 0)
            if rsi_ok and atr_expanding:
                return SELL

    return HOLD
