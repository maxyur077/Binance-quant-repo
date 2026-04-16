import pandas as pd

from azalyst.config import BUY, SELL, HOLD
from azalyst.candlestick import is_hammer, is_bullish_engulfing, is_bearish_engulfing, is_inverted_hammer

def signal(df: pd.DataFrame) -> int:
    if len(df) < 5:
        return HOLD

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # ── Global Armor Filter ──
    # 1. EMA 200 alignment
    ema_200 = last.get("ema_200", last["close"])
    
    # 2. Volume Displacement (Volume must be high during the FVG formation)
    vol_ma = last.get("vol_ma_20", 0)
    high_conviction_vol = last["volume"] > vol_ma * 1.2 if vol_ma > 0 else True

    # Check for Bullish FVG
    lookback = 15
    recent_df = df.tail(lookback)
    
    for i in range(2, len(recent_df) - 1):
        c1 = recent_df.iloc[i-2]
        c2 = recent_df.iloc[i-1] # Displacement candle
        c3 = recent_df.iloc[i]
        
        if c3["low"] > c1["high"]: # Bullish FVG
            fvg_top = c3["low"]
            fvg_bottom = c1["high"]
            
            # MSS Check: Did the move break a recent Swing High?
            swing_high = recent_df["high"].iloc[:i].max()
            mss_confirmed = c3["high"] > swing_high

            if last["low"] <= fvg_top and last["close"] >= fvg_bottom and mss_confirmed:
                # 3. Trend & Conviction Alignment
                if last["close"] > ema_200 and high_conviction_vol:
                    if is_hammer(last) or is_bullish_engulfing(last, prev):
                        return BUY
                        
    # Check for Bearish FVG
    for i in range(2, len(recent_df) - 1):
        c1 = recent_df.iloc[i-2]
        c2 = recent_df.iloc[i-1]
        c3 = recent_df.iloc[i]
        
        if c3["high"] < c1["low"]: # Bearish FVG
            fvg_bottom = c3["high"]
            fvg_top = c1["low"]
            
            # MSS Check: Did the move break a recent Swing Low?
            swing_low = recent_df["low"].iloc[:i].min()
            mss_confirmed = c3["low"] < swing_low

            if last["high"] >= fvg_bottom and last["close"] <= fvg_top and mss_confirmed:
                if last["close"] < ema_200 and high_conviction_vol:
                    if is_inverted_hammer(last) or is_bearish_engulfing(last, prev):
                        return SELL
                        
    return HOLD
