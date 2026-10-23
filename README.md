# X Sentiment + Price Forecasting Pipeline

A Python-based machine learning project that combines social media sentiment and historical market prices to explore short-horizon asset price forecasting.

The pipeline is designed to collect social media posts, analyze sentiment, retrieve recent news for contextual reporting, engineer time-series features, train forecasting models, and evaluate predictions using chronological walk-forward validation.

## Project Overview

Financial markets are influenced by many factors, including market trends, investor sentiment, and breaking news. This project explores whether sentiment extracted from X (formerly Twitter), combined with historical price data, can provide useful information for short-term price forecasting.

The project follows a modular workflow:

1. Collect social media posts using Apify.
2. Load historical posts from a CSV file.
3. Retrieve historical asset prices.
4. Calculate sentiment scores using VADER.
5. Engineer sentiment and price-based features.
6. Train separate machine learning models for multiple forecast horizons.
7. Evaluate predictions using walk-forward validation.
8. Generate forecast files, evaluation metrics, visualizations, and a sentiment summary.

**Important:** This is an experimental research and portfolio project, not a financial advisory system. Predictive performance must be established through appropriate out-of-sample evaluation.

## Key Features

- **Social media data ingestion:** Integrates with Apify for retrieving posts from X-compatible scraping workflows.
- **Historical data support:** Supports importing previously collected posts through CSV files.
- **Market data collection:** Retrieves historical price data using `yfinance`.
- **Sentiment analysis:** Uses VADER to generate sentiment scores from social media text.
- **Feature engineering:** Combines sentiment aggregates and historical price-derived features.
- **Multi-horizon forecasting:** Generates forecasts for horizons `n+0` through `n+5`.
- **Chronological validation:** Uses expanding-window walk-forward evaluation rather than randomly shuffling time-series observations.
- **News discovery:** Uses Tavily to retrieve recent news for contextual reporting.
- **Visual reporting:** Produces charts showing price and sentiment trends and a feature matrix.
- **Structured outputs:** Saves predictions, evaluation metrics, and a human-readable sentiment summary.
- **Modular Python architecture:** Separates configuration, ingestion, feature engineering, modeling, storage, reporting, and pipeline orchestration.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| pandas / NumPy | Data processing and numerical operations |
| scikit-learn | Machine learning and model evaluation |
| VADER Sentiment | Text sentiment scoring |
| Apify | Social media data ingestion |
| Tavily | Recent news discovery |
| yfinance | Historical market price data |
| SQLite | Local data storage |
| Matplotlib | Visualizations |
| python-dotenv | Environment-based configuration |

## Project Structure

```text
x_sentiment_price_pipeline/
│
├── data/
│   └── .gitkeep
│
├── outputs/
│   └── .gitkeep
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── storage.py
│   ├── ingest.py
│   ├── features.py
│   ├── model.py
│   ├── report.py
│   └── pipeline.py
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

The `data/` directory is intended for input data, while `outputs/` contains generated predictions, metrics, reports, and charts.

## Requirements

- Python 3.11 or newer recommended
- Git (optional, for cloning the repository)
- Internet connection for live data ingestion
- Your own API credentials for live Apify and Tavily integrations

## Installation

### 1. Clone the repository

Replace the example URL with your GitHub repository URL after publishing it.

```powershell
git clone YOUR_GITHUB_REPOSITORY_URL
cd x_sentiment_price_pipeline
```

Alternatively, download the repository as a ZIP file from GitHub and extract it.

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt instead:

```cmd
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## API Configuration

The live ingestion workflow may require external API credentials. **Users must provide their own keys; this repository does not include private credentials.**

### Apify

Apify is used to retrieve social media posts. Create an account at:

https://apify.com/

Generate an API token and select an actor compatible with your data collection requirements.

The expected actor input varies by actor. You may need to update `build_apify_input()` in `src/ingest.py` to match the selected actor's input schema.

### Tavily

Tavily is used to retrieve recent news for contextual reporting.

Create an account at:

https://tavily.com/

Obtain an API key if you want to enable the news integration.

### Configure environment variables

Create your local `.env` file from the provided example:

```powershell
Copy-Item .env.example .env
```

Open `.env` and fill in the required values using your own credentials and configuration.

Typical configuration variables include:

```dotenv
ASSET_SYMBOL=AAPL
ASSET_QUERY=Apple stock
APIFY_API_TOKEN=your_own_apify_token
APIFY_ACTOR_ID=your_selected_actor_id
TAVILY_API_KEY=your_own_tavily_api_key
```

Use the exact variable names expected by `src/config.py` and `.env.example` if they differ from the examples above.

**Security best practices**

- Never upload `.env` to GitHub.
- Never hardcode API keys into Python source files.
- Do not share private API credentials with recruiters.
- Review `.gitignore` before committing your project.
- Check the pricing, rate limits, and terms of the external data providers you use.

## Historical X Posts

The project supports loading previously collected posts from:

```text
data/historical_posts.csv
```

The required columns are:

| Column | Description |
|---|---|
| `created_at` | Post timestamp |
| `text` | Post text |

Optional columns may include:

- `post_id`
- `likes`
- `reposts`
- `views`
- `followers`
- `author_id`

Timestamps are normalized to UTC during processing.

If you use historical data, make sure you have the right to store, process, and redistribute it. Do not commit private or restricted datasets to a public repository.

## Running the Pipeline

After configuring your environment, the pipeline supports the following commands.

Run all stages:

```powershell
python -m src.pipeline all
```

Run ingestion:

```powershell
python -m src.pipeline ingest
```

Run training and forecasting:

```powershell
python -m src.pipeline train
```

**Note:** These commands describe the pipeline interface provided by the project. Successful execution depends on the availability and format of the input data, configuration, API credentials, and selected Apify actor. The live pipeline is not guaranteed to run without those dependencies being configured.

## Forecasting Approach

The project treats price forecasting as a supervised machine learning problem.

Separate models are designed to predict price targets at multiple horizons, from `n+0` through `n+5`.

The workflow includes:

1. Preparing chronological price and sentiment data.
2. Creating price-based and sentiment-based features.
3. Constructing target values for each forecast horizon.
4. Training models on earlier observations.
5. Evaluating predictions on later observations.
6. Comparing model errors with a simple persistence baseline.

The current implementation uses scikit-learn's `HistGradientBoostingRegressor` as a baseline model.

### Why supervised learning instead of reinforcement learning?

The objective is to estimate future prices from historical observations and engineered features. This is a supervised forecasting task.

Reinforcement learning would be more appropriate for a separate trading-policy problem involving explicit actions, transaction costs, execution assumptions, and reward functions. It is not necessary for this forecasting baseline.

## Evaluation Methodology

Random train-test splitting can produce misleading results for time-series data because it may allow information from the future to influence training.

This project uses chronological expanding-window walk-forward validation:

- Earlier observations form the training set.
- Later observations form the evaluation set.
- The training window expands as evaluation moves forward in time.
- Model predictions are compared with actual target values.
- A persistence baseline is included for comparison.

Evaluation metrics include:

- **MAE (Mean Absolute Error):** Average absolute prediction error.
- **RMSE (Root Mean Squared Error):** Error metric that penalizes larger errors more heavily.

### Important validation caveats

Forecast targets can overlap evaluation periods if the split strategy does not account for the target horizon. A robust implementation should purge training observations whose target windows overlap the test period.

Additionally, features must only use information that would have been available at the prediction timestamp. Social media engagement counts, delayed post ingestion, revised market data, and sentiment aggregates can introduce information leakage if handled incorrectly.

Model performance should not be presented as evidence of predictive ability until these issues have been checked and the evaluation has been verified.

## News and Sentiment

VADER provides a transparent baseline for scoring the sentiment of social media text.

The pipeline also supports retrieving recent news through Tavily for the human-readable report. In the current design, news is used for context rather than as a model input.

VADER is not specifically trained for financial language. Financial phrases, sarcasm, company-specific terminology, and market context may require a domain-specific sentiment model such as FinBERT in future iterations.

Sentiment is an exploratory feature, not a guarantee of future price direction.

## Outputs

The pipeline is designed to write generated artifacts to the `outputs/` directory.

| File | Description |
|---|---|
| `forecast.csv` | Forecasted prices for horizons `n+0` through `n+5` |
| `walk_forward_metrics.csv` | Out-of-sample MAE/RMSE and baseline comparisons |
| `walk_forward_predictions.csv` | Actual and predicted values from evaluation folds |
| `sentiment_price_timeline.png` | Visualization of price and sentiment over time |
| `sentiment_matrix.png` | Visualization of standardized features |
| `sentiment_summary.md` | Human-readable sentiment and market-context summary |

These files are generated artifacts; they may not exist until the relevant pipeline stages have run successfully.

## Limitations

This project is an experimental baseline and has several limitations:

- A short historical lookback can provide too few observations for reliable generalization.
- Social media data may be noisy, incomplete, delayed, or biased.
- VADER may not capture the meaning of financial language accurately.
- API availability, provider pricing, rate limits, and actor compatibility can affect ingestion.
- Historical engagement counts may not reflect the values available at the original post timestamp.
- Walk-forward evaluation must account for overlapping forecast targets and feature availability.
- Market prices are affected by many factors that are not included in this baseline.
- Forecasting errors do not directly measure the profitability of a trading strategy.
- The project does not account for trading costs, slippage, taxes, liquidity, or execution constraints.

No model performance, trading return, or financial advantage should be assumed without verified empirical results.

## Future Improvements

Potential next steps include:

- Integrating a finance-domain sentiment model such as FinBERT.
- Adding purged walk-forward validation for multi-step forecasting.
- Including confidence intervals or prediction intervals.
- Adding benchmark models and additional naive forecasting baselines.
- Testing different forecast horizons and lookback windows.
- Improving data-quality checks and missing-data handling.
- Adding automated tests and continuous integration.
- Supporting additional market data providers.
- Adding experiment tracking and reproducible configuration.
- Evaluating a trading policy separately, with realistic transaction costs, if strategy research becomes a goal.

## Reproducibility and Responsible Use

For reproducible results, document the selected asset, date range, data sources, feature definitions, model configuration, and evaluation procedure.

Respect the terms of service and licensing requirements of all data providers. This project is intended for research, education, and software demonstration. It is not investment advice and should not be used as the sole basis for financial decisions.

## Author

**Project:** X Sentiment + Price Forecasting Pipeline

**Focus areas:** Python, machine learning, sentiment analysis, time-series forecasting, API integration, data engineering, and model evaluation.

Add your name, GitHub profile, and contact details here if you want recruiters to contact you.

## License

Add a `LICENSE` file before distributing the repository publicly. If you have not selected a license, do not assume that others automatically have permission to reuse the code.
