import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

import numpy as np
import pandas as pd

from afp_mvp_v2.data_pipeline import load_inputs, prepare_dataset
from afp_mvp_v2.main import run_evaluate
from afp_mvp_v2.modeling import load_models, save_models, train_models
from afp_mvp_v2.recommendation import persist_recommendation, recommend_for_date


class TestAfpMvpV2(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.funds_csv = self.base / "funds.csv"
        self.market_csv = self.base / "market.csv"

        rng = np.random.default_rng(42)
        dates = pd.date_range("2024-01-01", periods=220, freq="D")
        funds = ["A", "B", "C"]

        rows = []
        for idx, fund in enumerate(funds):
            value = 1000 + idx * 40
            for d in dates:
                value *= 1 + rng.normal(0.0008 + idx * 0.0001, 0.008)
                rows.append({"date": d.date().isoformat(), "fund": fund, "value": round(value, 4)})
        pd.DataFrame(rows).to_csv(self.funds_csv, index=False)

        market = pd.DataFrame(
            {
                "date": [d.date().isoformat() for d in dates],
                "usdclp": 900 + rng.normal(0, 5, len(dates)),
                "sp500_ret": rng.normal(0.0005, 0.01, len(dates)),
                "tasa_local": 0.05 + rng.normal(0, 0.002, len(dates)),
                "news_sentiment": rng.normal(0, 0.3, len(dates)),
            }
        )
        market.to_csv(self.market_csv, index=False)

    def tearDown(self):
        self.tmp.cleanup()

    def test_train_predict_and_persist(self):
        funds_df, market_df = load_inputs(self.funds_csv, self.market_csv)
        prepared = prepare_dataset(funds_df, market_df)

        models = train_models(prepared)
        model_dir = self.base / "artifacts"
        save_models(models, model_dir)

        loaded_models = load_models(model_dir)
        rec = recommend_for_date(loaded_models, prepared.features, risk_profile="moderado")
        output_file = persist_recommendation(rec, self.base / "outputs")

        self.assertTrue(output_file.exists())
        self.assertIn(rec.recommended_fund, ["A", "B", "C"])
        self.assertGreaterEqual(rec.certainty_pct, 50.0)

    def test_evaluate_generates_files(self):
        args = Namespace(
            funds_csv=str(self.funds_csv),
            market_csv=str(self.market_csv),
            risk_profile="moderado",
            min_train_days=170,
            output_dir=str(self.base / "outputs_eval"),
        )

        run_evaluate(args)
        metrics_file = Path(args.output_dir) / "backtest_metrics.json"
        preds_file = Path(args.output_dir) / "backtest_predictions.csv"

        self.assertTrue(metrics_file.exists())
        self.assertTrue(preds_file.exists())

        metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
        self.assertGreater(metrics["days"], 0)


if __name__ == "__main__":
    unittest.main()
