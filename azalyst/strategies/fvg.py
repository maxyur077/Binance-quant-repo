import pandas as pd

from azalyst.config import BUY, SELL, HOLD
from azalyst.candlestick import is_hammer, is_bullish_engulfing, is_bearish_engulfing, is_inverted_hammer

def signal(df: pd.DataFrame) -> int:
    if len(df) < 5:
        return HOLD

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Look back over recent candles for a FVG that we are retracing into.
    # In a real system, you might track unfilled FVGs. Here we do an approximation over the last 10 candles.
    lookback = min(15, len(df))
    recent_df = df.tail(lookback)
    
    # Check for Bullish FVG
    for i in range(2, len(recent_df) - 1): # leaving room for current candle
        c1 = recent_df.iloc[i-2]
        c2 = recent_df.iloc[i-1] # displacement
        c3 = recent_df.iloc[i]
        
        # Bullish FVG criteria
        if c3["low"] > c1["high"]:
            fvg_top = c3["low"]
            fvg_bottom = c1["high"]
            
            # Are we in the FVG right now?
            if last["low"] <= fvg_top and last["close"] >= fvg_bottom:
                # In demand zone. Confirm with candlestick or indicators
                if is_hammer(last) or is_bullish_engulfing(last, prev):
                    if last["rsi_14"] < 60: # not overbought
                        return BUY
                        
    # Check for Bearish FVG
    for i in range(2, len(recent_df) - 1):
        c1 = recent_df.iloc[i-2]
        c2 = recent_df.iloc[i-1] # displacement down
        c3 = recent_df.iloc[i]
        
        # Bearish FVG criteria
        if c3["high"] < c1["low"]:
            fvg_bottom = c3["high"]
            fvg_top = c1["low"]
            
            # Are we in the FVG right now?
            if last["high"] >= fvg_bottom and last["close"] <= fvg_top:
                # In supply zone. Confirm with candlestick or indicators
                if is_inverted_hammer(last) or is_bearish_engulfing(last, prev):
                    if last["rsi_14"] > 40: # not oversold
                        return SELL
                        
    return HOLD
