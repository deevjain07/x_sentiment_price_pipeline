import json
from datetime import datetime, timedelta, timezone
import pandas as pd
import requests, yfinance as yf
from . import config
from .storage import init_db, upsert_posts, upsert_prices, upsert_news

def build_apify_input():
    # Adapt keys to the input schema of the Apify X scraper actor you choose.
    since = (datetime.now(timezone.utc)-timedelta(days=config.LOOKBACK_DAYS)).strftime("%Y-%m-%d")
    return {"searchTerms":[config.ASSET_QUERY], "start":since, "maxItems":config.APIFY_MAX_ITEMS, "sort":"Latest"}

def fetch_apify_posts():
    if not config.APIFY_API_TOKEN or not config.APIFY_ACTOR_ID:
        print("Apify credentials/actor not set; skipping live X scrape.")
        return pd.DataFrame()
    url=f"https://api.apify.com/v2/acts/{config.APIFY_ACTOR_ID}/run-sync-get-dataset-items"
    r=requests.post(url, params={"token":config.APIFY_API_TOKEN,"format":"json","clean":"true"},
                    json=build_apify_input(), timeout=180)
    r.raise_for_status()
    out=[]
    for x in r.json():
        author=x.get("author") if isinstance(x.get("author"),dict) else {}
        ts=x.get("createdAt") or x.get("created_at") or x.get("date") or x.get("timestamp")
        body=x.get("text") or x.get("fullText") or x.get("full_text") or x.get("content") or ""
        if not ts or not body: continue
        out.append({"post_id":str(x.get("id") or x.get("tweetId") or x.get("url") or ""),
          "created_at":pd.to_datetime(ts,utc=True,errors="coerce"),"text":body,
          "likes":x.get("likeCount",x.get("likes",0)),
          "reposts":x.get("retweetCount",x.get("reposts",x.get("retweets",0))),
          "views":x.get("viewCount",x.get("views",0)),
          "followers":author.get("followers",x.get("followersCount",x.get("followers",0))),
          "author_id":str(author.get("userName",x.get("username",""))),
          "source":"apify","raw_json":json.dumps(x,default=str)})
    df=pd.DataFrame(out)
    if not df.empty:
        df=df[df.created_at.notna()]
        empty=df.post_id.eq("")
        df.loc[empty,"post_id"]=df.loc[empty,"created_at"].astype(str)+"_"+df.loc[empty,"text"].str[:40]
    return df

def load_historical_posts():
    p=config.HISTORICAL_POSTS_PATH
    if not p.exists():
        print(f"No historical post CSV at {p}; skipping.")
        return pd.DataFrame()
    df=pd.read_csv(p)
    aliases={"date":"created_at","timestamp":"created_at","full_text":"text","retweets":"reposts",
             "followers_count":"followers","like_count":"likes","view_count":"views"}
    df=df.rename(columns={k:v for k,v in aliases.items() if k in df.columns})
    if "created_at" not in df or "text" not in df:
        raise ValueError("Historical CSV needs created_at and text columns.")
    df["created_at"]=pd.to_datetime(df.created_at,utc=True,errors="coerce")
    for c in ["likes","reposts","views","followers"]:
        if c not in df: df[c]=0
    if "post_id" not in df: df["post_id"]=df.created_at.astype(str)+"_"+df.text.astype(str).str[:40]
    df["source"]="historical_document"; df["raw_json"]="{}"
    return df[df.created_at.notna()]

def fetch_prices():
    end=datetime.now(timezone.utc); start=end-timedelta(days=config.LOOKBACK_DAYS+30)
    df=yf.download(config.ASSET_SYMBOL,start=start.date().isoformat(),
      end=(end+timedelta(days=1)).date().isoformat(),interval=config.PRICE_INTERVAL,
      auto_adjust=True,progress=False)
    if df.empty: raise RuntimeError("No price data. Check symbol, interval, provider limits, or connectivity.")
    if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
    df.index=pd.to_datetime(df.index,utc=True)
    return df[["Open","High","Low","Close","Volume"]].dropna(subset=["Close"])

def fetch_news():
    if not config.TAVILY_API_KEY:
        print("Tavily key not set; skipping news discovery.")
        return pd.DataFrame()
    r=requests.post("https://api.tavily.com/search",json={
      "api_key":config.TAVILY_API_KEY,"query":f"{config.ASSET_SYMBOL} latest news",
      "topic":"news","search_depth":"advanced","days":config.LOOKBACK_DAYS,
      "max_results":20,"include_answer":False},timeout=60)
    r.raise_for_status(); out=[]
    for x in r.json().get("results",[]):
        url=x.get("url","")
        out.append({"url":url,"published_at":x.get("published_date"),"title":x.get("title"),
          "content":x.get("content"),"source":url.split("/")[2] if url else ""})
    return pd.DataFrame(out)

def ingest_all():
    init_db(config.DATABASE_PATH)
    posts=pd.concat([load_historical_posts(),fetch_apify_posts()],ignore_index=True)
    if not posts.empty:
        posts["created_at"]=pd.to_datetime(posts.created_at,utc=True,errors="coerce")
        posts=posts.dropna(subset=["created_at","text"]).drop_duplicates("post_id",keep="last")
        posts=posts[posts.created_at >= pd.Timestamp.now(tz="UTC")-pd.Timedelta(days=config.LOOKBACK_DAYS)]
        upsert_posts(config.DATABASE_PATH,posts)
        print(f"Upserted {len(posts)} posts.")
    prices=fetch_prices(); upsert_prices(config.DATABASE_PATH,prices)
    news=fetch_news(); upsert_news(config.DATABASE_PATH,news)
    print(f"Stored {len(prices)} price bars and {len(news)} news results.")
