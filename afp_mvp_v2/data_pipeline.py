from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass
class PreparedData:
    features: pd.DataFrame
    funds: list[str]
    market_columns: list[str]


def load_inputs(funds_csv: str | Path, market_csv: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    funds_df = pd.read_csv(funds_csv)
    market_df = pd.read_csv(market_csv)

    required_fund_cols = {"date", "fund", "value"}
    missing_fund = required_fund_cols - set(funds_df.columns)
    if missing_fund:
        raise ValueError(f"funds CSV is missing required columns: {sorted(missing_fund)}")

    if "date" not in market_df.columns:
        raise ValueError("market CSV is missing required column: date")

    funds_df["date"] = pd.to_datetime(funds_df["date"])
    market_df["date"] = pd.to_datetime(market_df["date"])

    if "news_sentiment" not in market_df.columns:
        market_df["news_sentiment"] = 0.0

    return funds_df, market_df


def prepare_dataset(
    funds_df: pd.DataFrame,
    market_df: pd.DataFrame,
    lags: Iterable[int] = (1, 5, 20),
    volatility_window: int = 20,
) -> PreparedData:
    fund_values = (
        funds_df.pivot_table(index="date", columns="fund", values="value", aggfunc="last")
        .sort_index()
        .ffill()
    )
    daily_returns = fund_values.pct_change()

    market = market_df.sort_values("date").drop_duplicates("date", keep="last").set_index("date")
    market_cols = [c for c in market.columns if c != "date"]

    parts: list[pd.DataFrame] = []
    for fund in fund_values.columns:
        fund_frame = pd.DataFrame(index=fund_values.index)
        fund_frame["fund"] = fund
        fund_frame["value"] = fund_values[fund]
        fund_frame["ret_1d"] = daily_returns[fund]
        for lag in lags:
            fund_frame[f"ret_{lag}d"] = fund_values[fund].pct_change(lag)
        fund_frame["volatility"] = daily_returns[fund].rolling(volatility_window).std()
        fund_frame["momentum_5d"] = daily_returns[fund].rolling(5).mean()
        fund_frame["target_return"] = daily_returns[fund].shift(-1)
        fund_frame["target_up"] = (fund_frame["target_return"] > 0).astype(int)
        parts.append(fund_frame)

    merged = pd.concat(parts).reset_index().rename(columns={"index": "date"})
    merged = merged.merge(market.reset_index(), on="date", how="left")
    merged = merged.sort_values(["date", "fund"]).dropna(subset=["target_return"])

    feature_cols = [
        c
        for c in merged.columns
        if c
        not in {
            "date",
            "fund",
            "target_return",
            "target_up",
        }
    ]
    clean = merged.dropna(subset=feature_cols)
    return PreparedData(features=clean, funds=sorted(fund_values.columns.tolist()), market_columns=market_cols)
