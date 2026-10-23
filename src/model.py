import numpy as np
import pandas as pd

from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .features import FEATURES
from . import config


MAX_HORIZON = 5


def model_factory():
    return make_pipeline(
        SimpleImputer(strategy="median", add_indicator=True),
        HistGradientBoostingRegressor(
            max_iter=150,
            learning_rate=0.05,
            max_leaf_nodes=7,
            l2_regularization=1.0,
            random_state=7,
        ),
    )


def walk_forward(df, min_train=40, test_size=10, step=10):
    data = df.dropna(subset=["close"]).copy()
    X = data[FEATURES]

    preds = []
    metrics = []

    for start in range(min_train, len(data), step):
        end = min(start + test_size, len(data))
        test_idx = np.arange(start, end)

        # Purge training rows whose future targets could overlap
        # the first observation in the test fold.
        train_end = start - MAX_HORIZON
        if train_end <= 0:
            continue

        train_idx = np.arange(train_end)

        for h in range(MAX_HORIZON + 1):
            target = f"target_h{h}"

            tr = train_idx[
                data[target].iloc[train_idx].notna().to_numpy()
            ]
            te = test_idx[
                data[target].iloc[test_idx].notna().to_numpy()
            ]

            if len(tr) < min_train or len(te) == 0:
                continue

            model = model_factory()
            model.fit(X.iloc[tr], data[target].iloc[tr])

            predictions = model.predict(X.iloc[te])
            actual = data[target].iloc[te].to_numpy()
            baseline = data["close"].iloc[te].to_numpy()

            for ix, y, prediction, base in zip(
                te, actual, predictions, baseline
            ):
                preds.append(
                    {
                        "timestamp": data.index[ix],
                        "horizon": h,
                        "actual": y,
                        "prediction": prediction,
                        "naive_last_close": base,
                    }
                )

            metrics.append(
                {
                    "fold_start": str(data.index[te[0]]),
                    "horizon": h,
                    "n_test": len(te),
                    "mae": mean_absolute_error(actual, predictions),
                    "rmse": float(
                        np.sqrt(mean_squared_error(actual, predictions))
                    ),
                    "directional_accuracy": float(
                        np.mean(
                            np.sign(predictions - baseline)
                            == np.sign(actual - baseline)
                        )
                    ),
                    "baseline_mae": mean_absolute_error(actual, baseline),
                    "baseline_rmse": float(
                        np.sqrt(mean_squared_error(actual, baseline))
                    ),
                }
            )

    return pd.DataFrame(preds), pd.DataFrame(metrics)


def fit_latest_forecasts(df):
    data = df.dropna(subset=["close"]).copy()
    latest = data.iloc[[-1]]

    result = {
        "timestamp": str(data.index[-1]),
        "asset": config.ASSET_SYMBOL,
    }

    for h in range(MAX_HORIZON + 1):
        target = f"target_h{h}"
        valid = data.dropna(subset=[target])

        if len(valid) < 40:
            result[f"n+{h}"] = float("nan")
            continue

        model = model_factory()
        model.fit(valid[FEATURES], valid[target])
        result[f"n+{h}"] = float(
            model.predict(latest[FEATURES])[0]
        )

    return result
