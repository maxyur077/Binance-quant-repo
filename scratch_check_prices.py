import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from backtest.data import DataProvider

provider = DataProvider()
all_data, _ = provider.prepare_backtest_data(["ORCA/USDT:USDT"], pd.Timestamp("2026-06-09", tz="UTC"), pd.Timestamp("2026-06-11", tz="UTC"))
df = all_data["ORCA/USDT:USDT"]

print("ORCA prices around 2026-06-10:")
print(df.loc["2026-06-10 02:00":"2026-06-10 08:00", ["open", "high", "low", "close"]])
