from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

import pandas as pd

SignalType = Literal[1, -1, 0]  # BUY=1, SELL=-1, HOLD=0


class BaseStrategy(ABC):
    name: str

    @abstractmethod
    def signal(self, df: pd.DataFrame) -> SignalType:
        """
        Evaluate the dataframe and return a trading signal.
        Must return 1 (BUY), -1 (SELL), or 0 (HOLD).
        """
        ...
