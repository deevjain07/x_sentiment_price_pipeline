import sys
from . import config
from .ingest import ingest_all
from .features import build_frame
from .model import walk_forward,fit_latest_forecasts
from .report import make_reports

def train_and_report():
    df=build_frame()
    if len(df)<50: raise RuntimeError(f"Only {len(df)} aligned bars found; at least 50 are needed.")
    preds,metrics=walk_forward(df); forecast=fit_latest_forecasts(df)
    make_reports(df,preds,metrics,forecast)
    print("Outputs written to",config.OUTPUT_DIR)

def main():
    command=sys.argv[1] if len(sys.argv)>1 else "all"
    if command in ("ingest","all"): ingest_all()
    if command in ("train","report","all"): train_and_report()
    if command not in ("ingest","train","report","all"):
        raise SystemExit("Usage: python -m src.pipeline [ingest|train|report|all]")
if __name__=="__main__": main()
