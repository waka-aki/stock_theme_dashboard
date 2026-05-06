import math
from typing import Any

import pandas as pd
import yfinance as yf

from src.config import MIN_PRICE_ROWS
from src.metrics import calculate_price_metrics
from src.providers.base import StockData, StockDataProvider


FUNDAMENTAL_KEYS = {
    "market_cap": "marketCap",
    "per": "trailingPE",
    "pbr": "priceToBook",
    "roe": "returnOnEquity",
}


def to_yfinance_ticker(code: str) -> str:
    clean = str(code).strip()
    return clean if clean.endswith(".T") else f"{clean}.T"


def _safe_float(value: Any) -> float:
    if value is None:
        return float("nan")
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return number if math.isfinite(number) else float("nan")


class YFinanceProvider(StockDataProvider):
    def __init__(self, period: str = "8mo", min_rows: int = MIN_PRICE_ROWS) -> None:
        self.period = period
        self.min_rows = min_rows

    def fetch_stock(self, code: str) -> StockData:
        ticker_symbol = to_yfinance_ticker(code)
        status: list[str] = []
        history = pd.DataFrame()
        fundamentals = {
            "market_cap": float("nan"),
            "per": float("nan"),
            "pbr": float("nan"),
            "roe": float("nan"),
            "roic": float("nan"),
        }

        try:
            ticker = yf.Ticker(ticker_symbol)
            history = ticker.history(period=self.period, auto_adjust=False)
        except Exception as exc:
            status.append(f"価格取得失敗: {exc}")

        try:
            info = ticker.get_info() if "ticker" in locals() else {}
            for output_key, yf_key in FUNDAMENTAL_KEYS.items():
                fundamentals[output_key] = _safe_float(info.get(yf_key))
                if math.isnan(fundamentals[output_key]):
                    status.append(f"{output_key} 欠損")
            status.append("roic 未取得")
        except Exception as exc:
            status.append(f"ファンダメンタル取得失敗: {exc}")

        return StockData(
            code=str(code).zfill(4),
            ticker=ticker_symbol,
            history=history,
            fundamentals=fundamentals,
            status=status,
        )


def build_dashboard_data(watchlist: pd.DataFrame, provider: StockDataProvider | None = None) -> pd.DataFrame:
    provider = provider or YFinanceProvider()
    rows: list[dict[str, Any]] = []

    for item in watchlist.to_dict("records"):
        code = str(item.get("code", "")).zfill(4)
        row = {
            "category": item.get("category", ""),
            "subcategory": item.get("subcategory", ""),
            "code": code,
            "name": item.get("name", ""),
            "latest_price": float("nan"),
            "market_cap": float("nan"),
            "per": float("nan"),
            "pbr": float("nan"),
            "roe": float("nan"),
            "roic": float("nan"),
            "change_1d_pct": float("nan"),
            "change_5bd_pct": float("nan"),
            "change_25bd_pct": float("nan"),
            "change_75bd_pct": float("nan"),
            "data_status": "",
        }

        try:
            stock_data = provider.fetch_stock(code)
            price_metrics, price_status = calculate_price_metrics(stock_data.history, provider.min_rows)
            row.update(price_metrics)
            row.update(stock_data.fundamentals)
            statuses = [*stock_data.status, *price_status]
            row["data_status"] = " / ".join(dict.fromkeys(statuses)) if statuses else "OK"
        except Exception as exc:
            row["data_status"] = f"取得処理失敗: {exc}"

        rows.append(row)

    return pd.DataFrame(rows)

