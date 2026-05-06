from pathlib import Path
import os

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
WATCHLIST_PATH = DATA_DIR / "watchlist.csv"
DASHBOARD_DATA_PATH = DATA_DIR / "dashboard_data.csv"

load_dotenv(ROOT_DIR / ".env")

CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "21600"))
MIN_PRICE_ROWS = int(os.getenv("MIN_PRICE_ROWS", "100"))
