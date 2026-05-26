from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .modeling import TrainedModels


RISK_PROFILES = {
    "conservador": {"w_prob": 0.55, "w_ret": 0.20, "w_vol": 0.25},
    "moderado": {"w_prob": 0.40, "w_ret": 0.40, "w_vol": 0.20},
    "agresivo": {"w_prob": 0.25, "w_ret": 0.60, "w_vol": 0.15},
}
CERTAINTY_MARGIN_SCALE = 200.0


@dataclass
class DailyRecommendation:
    date: str
    risk_profile: str
    recommended_fund: str
    certainty_pct: float
    details: list[dict]


def _score(prob_up: float, expected_return: float, volatility: float, profile: str) -> float:
    cfg = RISK_PROFILES[profile]
    return (
        cfg["w_prob"] * prob_up
        + cfg["w_ret"] * expected_return
        - cfg["w_vol"] * max(volatility, 0.0)
    )


def recommend_for_date(
    models: TrainedModels,
    features: pd.DataFrame,
    risk_profile: str,
    as_of_date: str | None = None,
) -> DailyRecommendation:
    if risk_profile not in RISK_PROFILES:
        raise ValueError(f"Unknown risk profile '{risk_profile}'. Use one of: {sorted(RISK_PROFILES)}")

    frame = features.copy()
    if as_of_date:
        day = pd.to_datetime(as_of_date)
        frame = frame[frame["date"] == day]
    else:
        day = frame["date"].max()
        frame = frame[frame["date"] == day]

    if frame.empty:
        raise ValueError("No feature rows available for requested prediction date")

    rows = []
    for _, row in frame.iterrows():
        fund = row["fund"]
        if fund not in models.classifiers:
            continue
        x = row[models.feature_columns].to_frame().T
        prob_up = float(models.classifiers[fund].predict_proba(x)[0][1])
        expected_return = float(models.regressors[fund].predict(x)[0])
        volatility = float(row.get("volatility", 0.0))
        score = _score(prob_up, expected_return, volatility, risk_profile)
        rows.append(
            {
                "fund": fund,
                "prob_up": prob_up,
                "expected_return": expected_return,
                "volatility": volatility,
                "score": score,
            }
        )

    if not rows:
        raise ValueError("No trained fund models are compatible with the available feature rows")

    ranked = sorted(rows, key=lambda item: item["score"], reverse=True)
    top = ranked[0]
    second = ranked[1] if len(ranked) > 1 else ranked[0]
    margin = max(top["score"] - second["score"], 0.0)
    certainty_pct = float(np.clip(50.0 + margin * CERTAINTY_MARGIN_SCALE, 50.0, 99.0))

    return DailyRecommendation(
        date=str(pd.to_datetime(day).date()),
        risk_profile=risk_profile,
        recommended_fund=top["fund"],
        certainty_pct=certainty_pct,
        details=ranked,
    )


def persist_recommendation(rec: DailyRecommendation, output_dir: str | Path) -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    payload = {
        "date": rec.date,
        "risk_profile": rec.risk_profile,
        "recommended_fund": rec.recommended_fund,
        "certainty_pct": round(rec.certainty_pct, 2),
        "details": rec.details,
        "disclaimer": "Predictions are probabilistic estimates, not financial guarantees.",
    }

    dated_file = out / f"prediction_{rec.date}.json"
    dated_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    history_file = out / "predictions_history.csv"
    row = pd.DataFrame(
        [
            {
                "date": rec.date,
                "risk_profile": rec.risk_profile,
                "recommended_fund": rec.recommended_fund,
                "certainty_pct": round(rec.certainty_pct, 2),
            }
        ]
    )
    if history_file.exists():
        row.to_csv(history_file, mode="a", header=False, index=False)
    else:
        row.to_csv(history_file, index=False)

    return dated_file
