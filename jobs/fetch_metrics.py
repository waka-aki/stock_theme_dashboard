"""Fetch JP stock metrics via yfinance and upsert into Supabase.

Designed to run from GitHub Actions on a weekday schedule, but also works locally.
Requires the following environment variables:
  SUPABASE_URL                Project URL
  SUPABASE_SERVICE_ROLE_KEY   Service role key (bypasses RLS for writes)
"""

from __future__ import annotations

import math
import os
import sys
from datetime import date, timedelta
from typing import Any

import yfinance as yf
from supabase import Client, create_client


def to_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def fetch_distinct_codes(supabase: Client) -> list[str]:
    """Return distinct watchlist codes across all users (service role bypasses RLS)."""
    resp = supabase.table("watchlist").select("code").execute()
    return sorted({row["code"] for row in resp.data if row.get("code")})


def fetch_metrics_for_code(code: str) -> dict[str, Any] | None:
    """Return one metrics row for the given 4-digit code, or None on failure."""
    symbol = f"{code}.T"
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="6mo", auto_adjust=False)
    except Exception as exc:
        print(f"  ! {code}: history fetch failed: {exc}", file=sys.stderr)
        return None

    if hist is None or hist.empty or "Close" not in hist.columns:
        print(f"  ! {code}: no history data", file=sys.stderr)
        return None

    close = hist["Close"].dropna()
    if close.empty:
        print(f"  ! {code}: empty close series", file=sys.stderr)
        return None

    latest_price = to_optional_float(close.iloc[-1])
    if latest_price is None:
        return None

    def pct_n_trading_days(n: int) -> float | None:
        if len(close) < n + 1:
            return None
        past = to_optional_float(close.iloc[-(n + 1)])
        if past is None or past == 0:
            return None
        return (latest_price - past) / past * 100

    latest_date = close.index[-1].date()

    def pct_calendar_days(days: int) -> float | None:
        target = latest_date - timedelta(days=days)
        mask = close.index.date <= target
        subset = close[mask]
        if subset.empty:
            return None
        past = to_optional_float(subset.iloc[-1])
        if past is None or past == 0:
            return None
        return (latest_price - past) / past * 100

    info: dict[str, Any] = {}
    try:
        info = ticker.info or {}
    except Exception as exc:
        print(f"  ! {code}: info fetch failed: {exc}", file=sys.stderr)

    return {
        "code": code,
        "fetched_at": date.today().isoformat(),
        "price": latest_price,
        "market_cap": to_optional_float(info.get("marketCap")),
        "change_1bd": pct_n_trading_days(1),
        "change_2bd": pct_n_trading_days(2),
        "change_3bd": pct_n_trading_days(3),
        "change_5bd": pct_n_trading_days(5),
        "change_2w": pct_calendar_days(14),
        "change_1m": pct_calendar_days(30),
        "change_2m": pct_calendar_days(60),
        "change_3m": pct_calendar_days(90),
    }


def main() -> int:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set", file=sys.stderr)
        return 1

    supabase = create_client(url, key)

    codes = fetch_distinct_codes(supabase)
    if not codes:
        print("No watchlist entries. Nothing to fetch.")
        return 0

    print(f"Fetching metrics for {len(codes)} codes")
    rows: list[dict[str, Any]] = []
    for code in codes:
        print(f"  - {code}")
        row = fetch_metrics_for_code(code)
        if row is not None:
            rows.append(row)

    if not rows:
        print("All fetches failed. Nothing to upsert.", file=sys.stderr)
        return 1

    supabase.table("stock_metrics").upsert(
        rows, on_conflict="code,fetched_at"
    ).execute()
    print(f"Upserted {len(rows)} rows into stock_metrics")
    return 0


if __name__ == "__main__":
    sys.exit(main())
