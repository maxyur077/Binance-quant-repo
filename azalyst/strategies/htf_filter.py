import pandas as pd

def get_htf_trend(htf_df: pd.DataFrame) -> int:
    """
    Returns the macro trend based on the higher timeframe (e.g., 4H) dataframe.
    1 for Bullish, -1 for Bearish, 0 for Neutral.
    """
    if htf_df.empty or len(htf_df) < 200:
        return 0

    last = htf_df.iloc[-1]
    
    # Needs ema_50 and ema_200 precalculated on the htf_df
    if "ema_200" not in htf_df.columns or "ema_50" not in htf_df.columns or "adx" not in htf_df.columns:
        return 0

    ema_50 = last["ema_50"]
    ema_200 = last["ema_200"]
    htf_adx = last["adx"]
    price = last["close"]

    # ── Macro Chop Filter ──
    # If the 4H ADX is below 20, the macro market has no trend.
    if htf_adx < 20:
        return 0

    if price > ema_200 and ema_50 > ema_200:
        return 1
    elif price < ema_200 and ema_50 < ema_200:
        return -1
    
    return 0
