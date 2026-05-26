from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from .data_pipeline import PreparedData

MIN_TRAINING_SAMPLES = 60


@dataclass
class TrainedModels:
    classifiers: dict[str, RandomForestClassifier]
    regressors: dict[str, RandomForestRegressor]
    feature_columns: list[str]


def feature_columns(df: pd.DataFrame) -> list[str]:
    return [
        c
        for c in df.columns
        if c not in {"date", "fund", "target_return", "target_up"}
    ]


def train_models(prepared: PreparedData) -> TrainedModels:
    classifiers: dict[str, RandomForestClassifier] = {}
    regressors: dict[str, RandomForestRegressor] = {}
    fcols = feature_columns(prepared.features)

    for fund in prepared.funds:
        subset = prepared.features[prepared.features["fund"] == fund]
        if len(subset) < MIN_TRAINING_SAMPLES:
            continue

        x = subset[fcols]
        y_cls = subset["target_up"]
        y_reg = subset["target_return"]

        cls = RandomForestClassifier(
            n_estimators=80,
            random_state=42,
            min_samples_leaf=3,
            class_weight="balanced_subsample",
        )
        reg = RandomForestRegressor(
            n_estimators=80,
            random_state=42,
            min_samples_leaf=3,
        )
        cls.fit(x, y_cls)
        reg.fit(x, y_reg)
        classifiers[fund] = cls
        regressors[fund] = reg

    if not classifiers:
        raise ValueError(
            f"Not enough data to train models. Need at least {MIN_TRAINING_SAMPLES} rows per fund."
        )

    return TrainedModels(classifiers=classifiers, regressors=regressors, feature_columns=fcols)


def save_models(models: TrainedModels, output_dir: str | Path) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    with (out / "models.pkl").open("wb") as f:
        pickle.dump(models, f)

    metadata = {
        "funds": sorted(models.classifiers.keys()),
        "feature_columns": models.feature_columns,
    }
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def load_models(model_dir: str | Path) -> TrainedModels:
    path = Path(model_dir) / "models.pkl"
    with path.open("rb") as f:
        return pickle.load(f)
