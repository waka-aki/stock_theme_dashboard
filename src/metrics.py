import pandas as pd


CHANGE_WINDOWS = {
    "change_1d_pct": 1,
    "change_5bd_pct": 5,
    "change_25bd_pct": 25,
    "change_75bd_pct": 75,
}


def calculate_price_metrics(history: pd.DataFrame, min_rows: int = 100) -> tuple[dict[str, float], list[str]]:
    metrics: dict[str, float] = {
        "latest_price": float("nan"),
        "change_1d_pct": float("nan"),
        "change_5bd_pct": float("nan"),
        "change_25bd_pct": float("nan"),
        "change_75bd_pct": float("nan"),
    }
    status: list[str] = []

    if history is None or history.empty:
        return metrics, ["価格データなし"]

    price_col = "Close" if "Close" in history.columns else None
    if price_col is None:
        return metrics, ["Close列なし"]

    prices = pd.to_numeric(history[price_col], errors="coerce").dropna()
    if prices.empty:
        return metrics, ["終値データなし"]

    if len(prices) < min_rows:
        status.append(f"価格データ不足: {len(prices)}行")

    latest = prices.iloc[-1]
    metrics["latest_price"] = float(latest)

    for column, rows_back in CHANGE_WINDOWS.items():
        if len(prices) > rows_back:
            base = prices.iloc[-(rows_back + 1)]
            if pd.notna(base) and base != 0:
                metrics[column] = float(latest / base - 1)
            else:
                status.append(f"{rows_back}営業日前価格が無効")
        else:
            metrics[column] = float("nan")
            status.append(f"{rows_back}営業日比に必要な価格データ不足")

    return metrics, status


def category_return_summary(df: pd.DataFrame) -> pd.DataFrame:
    change_cols = list(CHANGE_WINDOWS.keys())
    if df.empty:
        return pd.DataFrame(columns=["category", *change_cols])
    return df.groupby("category", dropna=False)[change_cols].mean().reset_index()


def subcategory_summary(df: pd.DataFrame) -> pd.DataFrame:
    change_cols = list(CHANGE_WINDOWS.keys())
    if df.empty:
        return pd.DataFrame()

    grouped = df.groupby(["category", "subcategory"], dropna=False)
    summary = grouped.agg(code_count=("code", "count"))
    for col in change_cols:
        summary[f"{col}_mean"] = grouped[col].mean()
        summary[f"{col}_median"] = grouped[col].median()
    return summary.reset_index()

