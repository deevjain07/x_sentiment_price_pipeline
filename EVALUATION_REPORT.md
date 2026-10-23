# Model Evaluation Report
## X Sentiment and Price Prediction Pipeline

**Project:** `x_sentiment_price_pipeline`  
**Asset:** BTC-USD (configurable)  
**Evaluation status:** Pending empirical backtest results

## 1. Executive Summary

This project investigates whether social-media sentiment, combined with historical market prices, provides useful information for predicting future asset prices over horizons from n+0 to n+5.

The pipeline integrates data ingestion, feature engineering, SQLite storage, and machine-learning evaluation. This report is intended to assess predictive performance and, where a trading strategy is explicitly simulated, risk-adjusted returns.

**Important:** No verified backtest results are included in this version. Performance conclusions will be added after the pipeline has been run and its outputs checked.

## 2. Evaluation Methodology

The evaluation should use chronological, walk-forward testing rather than a random train/test split.

- **Prediction horizons:** n+0 through n+5.
- **Baseline:** A simple buy-and-hold or no-change forecast, as appropriate for the task.
- **Model comparison:** Compare the machine-learning model against the baseline on the same test dates.
- **Data integrity:** Use only information available at the prediction timestamp.
- **Leakage prevention:** Purge training observations whose forward target windows overlap the test period.
- **Transaction costs:** Include trading fees and slippage if evaluating a trading strategy.
- **Reproducibility:** Record the data period, feature set, model configuration, and evaluation settings.

The n+0 horizon may represent a nowcast rather than a genuinely future prediction. Its interpretation depends on when the features are available relative to the price being predicted.

## 3. Predictive Performance

Complete this table using the actual model evaluation outputs.

| Metric | Result |
|---|---:|
| Test period | Pending |
| Number of test observations | Pending |
| MAE | Pending |
| RMSE | Pending |
| Directional accuracy | Pending |
| Baseline performance | Pending |

MAE measures average absolute prediction error. RMSE penalizes larger errors more heavily. Directional accuracy measures how often predicted price direction matches the observed direction, provided the target is defined consistently.

## 4. Risk-Adjusted Strategy Performance

Sharpe Ratio, Sortino Ratio, and Maximum Drawdown evaluate a **trading strategy's returns**, not price-prediction errors by themselves. These metrics require a defined strategy and a series of realized or simulated portfolio returns.

| Risk metric | Result |
|---|---:|
| Sharpe Ratio | Pending |
| Sortino Ratio | Pending |
| Maximum Drawdown | Pending |
| Annualized strategy return | Pending |
| Annualized volatility | Pending |
| Number of trades | Pending |
| Transaction costs | Pending |

### Sharpe Ratio

Measures excess return relative to total return volatility.

\[
\text{Sharpe} =
\frac{\text{Mean periodic return} - \text{Risk-free periodic return}}
{\text{Standard deviation of periodic returns}}
\]

Annualization must match the return frequency. For daily returns, a common convention uses \(\sqrt{252}\) for annualization, but the convention and market calendar should be documented.

### Sortino Ratio

Measures excess return relative to downside deviation, using a clearly defined minimum acceptable return.

\[
\text{Sortino} =
\frac{\text{Mean periodic return} - \text{Target return}}
{\text{Downside deviation}}
\]

The target return and downside-deviation calculation must be specified.

### Maximum Drawdown

Measures the largest peak-to-trough decline in portfolio value over the evaluation period.

\[
\text{Drawdown}_t =
\frac{\text{Equity}_t}{\text{Running peak}_t}-1
\]

Maximum drawdown is the minimum value of this drawdown series. Report it as a percentage and state the evaluation period.

## 5. Results and Interpretation

**Status: Awaiting measured results.**

Once the evaluation is complete, this section should explain:

1. Whether the model improves on the baseline.
2. Which prediction horizon performs best and whether that result is stable.
3. Whether any simulated strategy remains profitable after transaction costs.
4. Whether returns are accompanied by acceptable volatility and drawdown.
5. Whether performance persists across different market conditions.

A high predictive accuracy does not necessarily imply profitable trading performance. Results should be interpreted alongside costs, risk, and out-of-sample stability.

## 6. Limitations

- Social-media coverage may be incomplete, noisy, or biased.
- Sentiment data availability and API limits may affect reproducibility.
- Historical relationships may not persist in future markets.
- A short or single-regime test period may produce misleading results.
- Trading fees, slippage, liquidity, and execution delays can reduce returns.
- Any look-ahead bias or target leakage can invalidate reported performance.
- Results on BTC-USD should not automatically be generalized to other assets.

## 7. Conclusion

The pipeline provides a framework for investigating the relationship between social sentiment and asset-price movements. Its predictive value and risk-adjusted trading performance remain unverified until chronological out-of-sample evaluation is completed.

**Next step:** Run the pipeline, inspect its generated predictions and metrics, and populate this report with reproducible results. Do not present pending metrics as established performance.

---

*This report is for research and educational purposes. Historical or simulated performance does not guarantee future results and is not financial advice.*
