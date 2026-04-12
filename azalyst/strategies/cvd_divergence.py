import pandas as pd

from azalyst.config import BUY, SELL, HOLD

def signal(df: pd.DataFrame) -> int:
    if len(df) < 20 or "cvd" not in df.columns:
        return HOLD

    last = df.iloc[-1]
    
    # Look back over recent bars
    recent_price_lows = df["low"].tail(10).min()
    prev_price_lows = df["low"].iloc[-20:-10].min()
    
    recent_cvd_lows = df["cvd"].tail(10).min()
    prev_cvd_lows = df["cvd"].iloc[-20:-10].min()

    # Bullish Divergence: Price making lower lows, but CVD making higher lows
    if recent_price_lows < prev_price_lows and recent_cvd_lows > prev_cvd_lows:
        # We need an entry trigger (e.g. price pushes back up over ema 9)
        if last["close"] > last["ema_9"] and df.iloc[-2]["close"] <= df.iloc[-2]["ema_9"]:
            return BUY
            
    recent_price_highs = df["high"].tail(10).max()
    prev_price_highs = df["high"].iloc[-20:-10].max()
    
    recent_cvd_highs = df["cvd"].tail(10).max()
    prev_cvd_highs = df["cvd"].iloc[-20:-10].max()

    # Bearish Divergence: Price making higher highs, but CVD making lower highs
    if recent_price_highs > prev_price_highs and recent_cvd_highs < prev_cvd_highs:
        if last["close"] < last["ema_9"] and df.iloc[-2]["close"] >= df.iloc[-2]["ema_9"]:
            return SELL

    return HOLD
