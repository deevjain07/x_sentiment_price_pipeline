import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
ASSET_SYMBOL = os.getenv("ASSET_SYMBOL", "BTC-USD")
ASSET_QUERY = os.getenv("ASSET_QUERY", "BTC OR Bitcoin OR $BTC")
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "180"))
PRICE_INTERVAL = os.getenv("PRICE_INTERVAL", "1d")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")
APIFY_ACTOR_ID = os.getenv("APIFY_ACTOR_ID", "")
APIFY_MAX_ITEMS = int(os.getenv("APIFY_MAX_ITEMS", "10000"))
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
HISTORICAL_POSTS_PATH = Path(os.getenv("HISTORICAL_POSTS_PATH", "data/historical_posts.csv"))
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "data/pipeline.db"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "outputs"))
