# AFP Recommendation MVP v2

> **Important**: this module provides probabilistic estimates for decision support only.
> It does **not** guarantee gains or prevent losses.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r afp_mvp_v2/requirements.txt
```

## Expected CSV format

### `funds.csv`
Long format with one row per fund/date:

| date | fund | value |
|---|---|---|
| 2025-01-02 | A | 1000.12 |
| 2025-01-02 | B | 998.40 |

- `date`: ISO date `YYYY-MM-DD`
- `fund`: fund id/name (A, B, C, D, E, etc.)
- `value`: daily cuota/value

### `market.csv`
Rows by date with market context features:

| date | usdclp | sp500_ret | tasa_local | news_sentiment |
|---|---|---|---|---|
| 2025-01-02 | 945.3 | 0.004 | 0.052 | -0.15 |

- `news_sentiment` is optional; if absent it defaults to `0.0` (placeholder).

## Commands

Train models:

```bash
python main.py train --funds-csv /path/funds.csv --market-csv /path/market.csv --model-dir afp_mvp_v2/artifacts
```

Daily recommendation:

```bash
python main.py predict --funds-csv /path/funds.csv --market-csv /path/market.csv --model-dir afp_mvp_v2/artifacts --risk-profile moderado
```

Backtesting/evaluation:

```bash
python main.py evaluate --funds-csv /path/funds.csv --market-csv /path/market.csv --risk-profile conservador --output-dir afp_mvp_v2/outputs
```

Automated retraining flow (scriptable by cron):

```bash
python main.py retrain --funds-csv /path/funds.csv --market-csv /path/market.csv --model-dir afp_mvp_v2/artifacts --output-dir afp_mvp_v2/outputs
```

## Output files

- `afp_mvp_v2/artifacts/models.pkl`: trained fund models
- `afp_mvp_v2/artifacts/metadata.json`: model metadata
- `afp_mvp_v2/outputs/prediction_<date>.json`: daily recommendation and certainty
- `afp_mvp_v2/outputs/predictions_history.csv`: recommendation history
- `afp_mvp_v2/outputs/backtest_predictions.csv`: backtest daily decisions vs realized returns
- `afp_mvp_v2/outputs/backtest_metrics.json`: evaluation summary

## Recommendation score

For each fund:

`score = w_prob * P(up) + w_ret * expected_return - w_vol * volatility`

Risk profiles:
- `conservador`: stronger volatility penalty
- `moderado`: balanced
- `agresivo`: stronger expected-return weight
