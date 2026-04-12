import pandas as pd

def is_bullish_engulfing(last: pd.Series, prev: pd.Series) -> bool:
    return (last["close"] > last["open"] and
            prev["close"] < prev["open"] and
            last["close"] >= prev["open"] and
            last["open"] <= prev["close"])

def is_bearish_engulfing(last: pd.Series, prev: pd.Series) -> bool:
    return (last["close"] < last["open"] and
            prev["close"] > prev["open"] and
            last["close"] <= prev["open"] and
            last["open"] >= prev["close"])

def is_hammer(last: pd.Series) -> bool:
    body_size = abs(last["close"] - last["open"])
    lower_wick = min(last["close"], last["open"]) - last["low"]
    upper_wick = last["high"] - max(last["close"], last["open"])
    return lower_wick > 2 * body_size and upper_wick < body_size

def is_inverted_hammer(last: pd.Series) -> bool:
    body_size = abs(last["close"] - last["open"])
    lower_wick = min(last["close"], last["open"]) - last["low"]
    upper_wick = last["high"] - max(last["close"], last["open"])
    return upper_wick > 2 * body_size and lower_wick < body_size
