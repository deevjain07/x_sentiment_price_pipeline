from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from . import config

def make_reports(df,predictions,metrics,forecast):
    out=config.OUTPUT_DIR; out.mkdir(parents=True,exist_ok=True)
    predictions.to_csv(out/"walk_forward_predictions.csv",index=False)
    metrics.to_csv(out/"walk_forward_metrics.csv",index=False)
    pd.DataFrame([forecast]).to_csv(out/"forecast.csv",index=False)
    fig,ax1=plt.subplots(figsize=(13,5))
    ax1.plot(df.index,df.close,label="Close price"); ax1.set_ylabel("Price")
    ax2=ax1.twinx(); ax2.plot(df.index,df.sentiment_mean,label="Mean X sentiment",alpha=.7)
    ax2.axhline(0,linewidth=1,alpha=.4); ax2.set_ylabel("VADER compound sentiment")
    ax1.set_title(f"{config.ASSET_SYMBOL}: price and X sentiment")
    fig.tight_layout(); fig.savefig(out/"sentiment_price_timeline.png",dpi=150); plt.close(fig)
    cols=["sentiment_mean","sentiment_change","post_count","log_return","volatility_5"]
    mat=df[cols].tail(60).copy(); mat=(mat-mat.mean())/mat.std().replace(0,1)
    fig,ax=plt.subplots(figsize=(13,5)); ax.imshow(mat.fillna(0).T,aspect="auto",interpolation="nearest")
    ax.set_yticks(range(len(cols)),labels=cols)
    step=max(1,len(mat)//8); ax.set_xticks(range(0,len(mat),step))
    ax.set_xticklabels([str(x.date()) for x in mat.index[::step]],rotation=45,ha="right")
    ax.set_title("Standardized sentiment / price feature matrix (last 60 bars)")
    fig.tight_layout(); fig.savefig(out/"sentiment_matrix.png",dpi=150); plt.close(fig)
    recent=df.tail(7); s=float(recent.sentiment_mean.mean())
    delta=float(recent.sentiment_mean.iloc[-1]-recent.sentiment_mean.iloc[0]) if len(recent)>1 else 0
    vol=int(recent.post_count.sum()); price=float(recent.close.iloc[-1])
    outlook="positive" if s>.05 else "negative" if s<-.05 else "neutral/mixed"
    trend="improving" if delta>.02 else "deteriorating" if delta<-.02 else "roughly stable"
    summary=f"""# {config.ASSET_SYMBOL} — sentiment outlook

**As of:** {df.index[-1]} (UTC)  
**Latest close:** {price:.6g}  
**Recent X sentiment:** {outlook} (7-bar mean VADER compound score: {s:.3f})  
**Sentiment direction:** {trend} (recent first-to-last change: {delta:+.3f})  
**Observed posts in recent window:** {vol}

## Interpretation
Descriptive only, not a buy/sell recommendation. Neutral sentiment may reflect mixed posts or low coverage. Social sentiment is noisy and may react to price rather than lead it. News is stored for context but excluded from model inputs to preserve the sentiment-and-price-only design.

## Forecasts
"""+"\n".join([f"- **n+{h}:** {forecast.get(f'n+{h}',float('nan')):.6g}" for h in range(6)])
    if not metrics.empty:
        summary+="\n\n## Walk-forward validation (mean across folds)\n\n"+metrics.groupby("horizon")[["mae","rmse","baseline_mae","baseline_rmse"]].mean().round(4).to_markdown()
    summary+="\n\n## Caveats\n180 days of daily data is a small sample. Source coverage, engagement-counter timing, regime changes, and data gaps can materially affect results. Compare with the last-close baseline and validate before use."
    (out/"sentiment_summary.md").write_text(summary,encoding="utf-8")
