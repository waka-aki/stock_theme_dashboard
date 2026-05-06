from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd


@dataclass
class StockData:
    code: str
    ticker: str
    history: pd.DataFrame
    fundamentals: dict[str, float]
    status: list[str]


class StockDataProvider(ABC):
    @abstractmethod
    def fetch_stock(self, code: str) -> StockData:
        """Fetch price history and fundamentals for one stock code."""

