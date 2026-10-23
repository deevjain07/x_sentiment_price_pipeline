import sqlite3, json
from pathlib import Path
import pandas as pd

def connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute("PRAGMA journal_mode=WAL")
    return con

def init_db(path):
    with connect(path) as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS posts(post_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, text TEXT,
          likes REAL, reposts REAL, views REAL, followers REAL, author_id TEXT, source TEXT, raw_json TEXT);
        CREATE TABLE IF NOT EXISTS prices(timestamp TEXT PRIMARY KEY, open REAL, high REAL, low REAL, close REAL, volume REAL);
        CREATE TABLE IF NOT EXISTS news(url TEXT PRIMARY KEY, published_at TEXT, title TEXT, content TEXT, source TEXT);
        """)

def upsert_posts(path, df):
    if df.empty: return
    cols = ["post_id","created_at","text","likes","reposts","views","followers","author_id","source","raw_json"]
    d = df.copy()
    for c in cols:
        if c not in d: d[c] = None
    d = d[cols]
    d["raw_json"] = d["raw_json"].map(lambda x: x if isinstance(x,str) else json.dumps(x, default=str))
    with connect(path) as con:
        d.to_sql("_posts_in", con, if_exists="replace", index=False)
        con.execute("INSERT OR REPLACE INTO posts SELECT * FROM _posts_in")
        con.execute("DROP TABLE _posts_in")

def upsert_prices(path, df):
    if df.empty: return
    d = df.copy().reset_index()
    d = d.rename(columns={d.columns[0]:"timestamp"})
    d["timestamp"] = pd.to_datetime(d["timestamp"], utc=True).astype(str)
    d = d[["timestamp","Open","High","Low","Close","Volume"]]
    d.columns = ["timestamp","open","high","low","close","volume"]
    with connect(path) as con:
        d.to_sql("_prices_in", con, if_exists="replace", index=False)
        con.execute("INSERT OR REPLACE INTO prices SELECT * FROM _prices_in")
        con.execute("DROP TABLE _prices_in")

def upsert_news(path, df):
    if df.empty: return
    d = df.copy()
    for c in ["url","published_at","title","content","source"]:
        if c not in d: d[c] = None
    d = d[["url","published_at","title","content","source"]]
    with connect(path) as con:
        d.to_sql("_news_in", con, if_exists="replace", index=False)
        con.execute("INSERT OR REPLACE INTO news SELECT * FROM _news_in")
        con.execute("DROP TABLE _news_in")

def read_table(path, table):
    with connect(path) as con:
        return pd.read_sql_query(f"SELECT * FROM {table}", con)
