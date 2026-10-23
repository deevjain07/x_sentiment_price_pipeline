import numpy as np, pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from . import config
from .storage import read_table

FEATURES=["sentiment_mean","sentiment_std","positive_share","negative_share","post_count",
 "engagement_sum","follower_weighted_sentiment","sentiment_change","log_return",
 "return_lag_1","return_lag_2","return_lag_3","return_lag_5","volatility_5",
 "volatility_20","ma_gap_5","ma_gap_20","bar_range"]

def build_frame():
    posts=read_table(config.DATABASE_PATH,"posts")
    prices=read_table(config.DATABASE_PATH,"prices")
    if prices.empty: raise RuntimeError("No prices in database. Run ingest first.")
    prices["timestamp"]=pd.to_datetime(prices.timestamp,utc=True)
    prices=prices.sort_values("timestamp").set_index("timestamp")
    for c in ["open","high","low","close","volume"]: prices[c]=pd.to_numeric(prices[c],errors="coerce")
    if posts.empty: agg=pd.DataFrame(index=prices.index)
    else:
        posts["created_at"]=pd.to_datetime(posts.created_at,utc=True,errors="coerce")
        posts=posts.dropna(subset=["created_at","text"])
        analyzer=SentimentIntensityAnalyzer()
        posts["sentiment"]=posts.text.astype(str).map(lambda t:analyzer.polarity_scores(t)["compound"])
        for c in ["likes","reposts","views","followers"]:
            posts[c]=pd.to_numeric(posts[c],errors="coerce").fillna(0).clip(lower=0)
        posts["engagement"]=posts.likes+2*posts.reposts+0.01*posts.views
        posts["weighted_sentiment"]=posts.sentiment*np.log1p(posts.followers)
        # Daily bar buckets align on UTC day. Adjust for non-daily exchange/session bars if needed.
        posts["timestamp"]=posts.created_at.dt.floor("1D" if config.PRICE_INTERVAL.endswith("d") else config.PRICE_INTERVAL)
        agg=posts.groupby("timestamp").agg(
          sentiment_mean=("sentiment","mean"),sentiment_std=("sentiment","std"),
          positive_share=("sentiment",lambda s:(s>.05).mean()),
          negative_share=("sentiment",lambda s:(s<-.05).mean()),post_count=("sentiment","size"),
          engagement_sum=("engagement","sum"),follower_weighted_sentiment=("weighted_sentiment","sum"))
    df=prices.join(agg,how="left")
    defaults={"sentiment_mean":0,"sentiment_std":0,"positive_share":0,"negative_share":0,
      "post_count":0,"engagement_sum":0,"follower_weighted_sentiment":0}
    for c,v in defaults.items():
        if c not in df: df[c]=v
        df[c]=df[c].fillna(v)
    df["log_return"]=np.log(df.close).diff()
    for lag in [1,2,3,5]: df[f"return_lag_{lag}"]=df.log_return.shift(lag)
    df["volatility_5"]=df.log_return.rolling(5).std()
    df["volatility_20"]=df.log_return.rolling(20).std()
    df["ma_gap_5"]=df.close/df.close.rolling(5).mean()-1
    df["ma_gap_20"]=df.close/df.close.rolling(20).mean()-1
    df["bar_range"]=(df.high-df.low)/df.close.replace(0,np.nan)
    df["sentiment_change"]=df.sentiment_mean.diff()
    for h in range(6): df[f"target_h{h}"]=df.close.shift(-h)
    return df.replace([np.inf,-np.inf],np.nan)
