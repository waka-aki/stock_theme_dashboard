from datetime import datetime
from pathlib import Path
import sys
from zoneinfo import ZoneInfo


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.config import DASHBOARD_DATA_PATH, WATCHLIST_PATH  # noqa: E402
from src.data_loader import load_watchlist, save_dashboard_snapshot  # noqa: E402
from src.providers.yfinance_provider import build_dashboard_data  # noqa: E402


def main() -> int:
    watchlist = load_watchlist(WATCHLIST_PATH)
    if watchlist.empty:
        print(f"Watchlist is empty: {WATCHLIST_PATH}")
        return 1

    dashboard_data = build_dashboard_data(watchlist)
    save_dashboard_snapshot(dashboard_data, DASHBOARD_DATA_PATH)

    updated_at = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"Updated {len(dashboard_data)} rows at {updated_at}")
    print(f"Saved: {DASHBOARD_DATA_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
