from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

import pandas as pd

from .data_pipeline import load_inputs, prepare_dataset
from .modeling import load_models, save_models, train_models
from .recommendation import persist_recommendation, recommend_for_date


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AFP daily recommendation MVP v2")
    sub = parser.add_subparsers(dest="command", required=True)

    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument("--funds-csv", required=True, help="CSV with columns: date,fund,value")
    shared.add_argument("--market-csv", required=True, help="CSV with date and market features")

    train_p = sub.add_parser("train", parents=[shared], help="Train fund models")
    train_p.add_argument("--model-dir", default="afp_mvp_v2/artifacts")

    predict_p = sub.add_parser("predict", parents=[shared], help="Predict and recommend one fund")
    predict_p.add_argument("--model-dir", default="afp_mvp_v2/artifacts")
    predict_p.add_argument("--risk-profile", default="moderado", choices=["conservador", "moderado", "agresivo"])
    predict_p.add_argument("--as-of-date", help="Date YYYY-MM-DD. Defaults to latest date")
    predict_p.add_argument("--output-dir", default="afp_mvp_v2/outputs")

    eval_p = sub.add_parser("evaluate", parents=[shared], help="Backtest recommendation strategy")
    eval_p.add_argument("--risk-profile", default="moderado", choices=["conservador", "moderado", "agresivo"])
    eval_p.add_argument("--min-train-days", type=int, default=120)
    eval_p.add_argument("--output-dir", default="afp_mvp_v2/outputs")

    retrain_p = sub.add_parser("retrain", parents=[shared], help="Train and evaluate in one command")
    retrain_p.add_argument("--model-dir", default="afp_mvp_v2/artifacts")
    retrain_p.add_argument("--risk-profile", default="moderado", choices=["conservador", "moderado", "agresivo"])
    retrain_p.add_argument("--min-train-days", type=int, default=120)
    retrain_p.add_argument("--output-dir", default="afp_mvp_v2/outputs")

    return parser


def _load_prepared(args: argparse.Namespace):
    funds_df, market_df = load_inputs(args.funds_csv, args.market_csv)
    return prepare_dataset(funds_df, market_df)


def run_train(args: argparse.Namespace) -> None:
    prepared = _load_prepared(args)
    models = train_models(prepared)
    save_models(models, args.model_dir)
    print(json.dumps({"status": "trained", "funds": sorted(models.classifiers)}, indent=2))


def run_predict(args: argparse.Namespace) -> None:
    prepared = _load_prepared(args)
    models = load_models(args.model_dir)
    rec = recommend_for_date(models, prepared.features, args.risk_profile, args.as_of_date)
    output_file = persist_recommendation(rec, args.output_dir)
    print(
        json.dumps(
            {
                "date": rec.date,
                "recommended_fund": rec.recommended_fund,
                "certainty_pct": round(rec.certainty_pct, 2),
                "risk_profile": rec.risk_profile,
                "output": str(output_file),
                "note": "Probabilistic recommendation, not guaranteed.",
            },
            indent=2,
        )
    )


def run_evaluate(args: argparse.Namespace) -> None:
    prepared = _load_prepared(args)
    dates = sorted(prepared.features["date"].unique())
    records: list[dict] = []

    for i in range(args.min_train_days, len(dates) - 1):
        cutoff = dates[i]
        train_rows = prepared.features[prepared.features["date"] < cutoff]
        pred_rows = prepared.features[prepared.features["date"] == cutoff]

        if train_rows.empty or pred_rows.empty:
            continue

        train_like = replace(prepared, features=train_rows)
        try:
            models = train_models(train_like)
            rec = recommend_for_date(models, pred_rows, args.risk_profile)
        except ValueError:
            continue

        realized = pred_rows[pred_rows["fund"] == rec.recommended_fund]["target_return"]
        if realized.empty:
            continue
        realized_return = float(realized.iloc[0])
        records.append(
            {
                "date": str(pd.to_datetime(cutoff).date()),
                "recommended_fund": rec.recommended_fund,
                "certainty_pct": round(rec.certainty_pct, 2),
                "realized_return": realized_return,
                "hit": int(realized_return > 0),
            }
        )

    if not records:
        raise ValueError("No backtest results. Use more data or lower --min-train-days.")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pred_file = out_dir / "backtest_predictions.csv"
    pd.DataFrame(records).to_csv(pred_file, index=False)

    returns = pd.Series([r["realized_return"] for r in records])
    metrics = {
        "days": len(records),
        "hit_rate": float(pd.Series([r["hit"] for r in records]).mean()),
        "avg_realized_return": float(returns.mean()),
        "cumulative_return": float((1.0 + returns).prod() - 1.0),
        "risk_profile": args.risk_profile,
        "disclaimer": "Backtest and forecasts are probabilistic and do not guarantee future returns.",
    }
    metrics_file = out_dir / "backtest_metrics.json"
    metrics_file.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(json.dumps({"predictions": str(pred_file), "metrics": str(metrics_file), **metrics}, indent=2))


def run_retrain(args: argparse.Namespace) -> None:
    run_train(args)
    eval_args = argparse.Namespace(
        funds_csv=args.funds_csv,
        market_csv=args.market_csv,
        risk_profile=args.risk_profile,
        min_train_days=args.min_train_days,
        output_dir=args.output_dir,
    )
    run_evaluate(eval_args)


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "train":
        run_train(args)
    elif args.command == "predict":
        run_predict(args)
    elif args.command == "evaluate":
        run_evaluate(args)
    elif args.command == "retrain":
        run_retrain(args)


if __name__ == "__main__":
    main()
