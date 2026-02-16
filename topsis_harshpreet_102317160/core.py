from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple
import math

import pandas as pd


class TopsisError(Exception):
    """Base exception for TOPSIS errors."""


class InputError(TopsisError):
    """Raised for invalid CLI/user inputs."""


@dataclass(frozen=True)
class TopsisResult:
    dataframe: pd.DataFrame
    score_col: str = "Topsis Score"
    rank_col: str = "Rank"


def _parse_csv_list(raw: str, kind: str) -> List[str]:
    if raw is None:
        raise InputError(f"{kind} is missing.")
    if "," not in raw:
        raise InputError(f"{kind} must be separated by ',' (comma).")
    parts = [p.strip() for p in raw.split(",")]
    if any(p == "" for p in parts):
        raise InputError(f"{kind} contains empty value(s).")
    return parts


def parse_weights(raw: str) -> List[float]:
    parts = _parse_csv_list(raw, "Weights")
    weights: List[float] = []
    for p in parts:
        try:
            w = float(p)
        except ValueError as e:
            raise InputError("Weights must be numeric values only.") from e
        if not math.isfinite(w):
            raise InputError("Weights must be finite numeric values.")
        if w <= 0:
            raise InputError("Weights must be > 0.")
        weights.append(w)
    return weights


def parse_impacts(raw: str) -> List[str]:
    parts = _parse_csv_list(raw, "Impacts")
    impacts: List[str] = []
    for p in parts:
        p2 = p.strip()
        if p2 in {"+", "positive", "pos", "+ve", "+v", "benefit"}:
            impacts.append("+")
        elif p2 in {"-", "negative", "neg", "-ve", "-v", "cost"}:
            impacts.append("-")
        else:
            raise InputError("Impacts must be either +ve or -ve (use '+' or '-').")
    return impacts


def validate_input_dataframe(df: pd.DataFrame) -> None:
    if df.shape[1] < 3:
        raise InputError("Input file must contain three or more columns.")
    numeric_part = df.iloc[:, 1:]
    coerced = numeric_part.apply(pd.to_numeric, errors="coerce")
    if coerced.isna().any().any():
        raise InputError("From 2nd to last columns must contain numeric values only.")
    df.iloc[:, 1:] = coerced


def topsis(df: pd.DataFrame, weights: Sequence[float], impacts: Sequence[str]) -> TopsisResult:
    validate_input_dataframe(df)

    m = df.shape[1] - 1  # number of criteria
    if len(weights) != m or len(impacts) != m:
        raise InputError(
            "The number of weights, number of impacts and number of columns (from 2nd to last columns) must be the same."
        )

    wsum = float(sum(weights))
    if wsum <= 0 or not math.isfinite(wsum):
        raise InputError("Weights sum must be finite and > 0.")
    w = [float(x) / wsum for x in weights]

    X = df.iloc[:, 1:].astype(float).to_numpy()
    denom = (X ** 2).sum(axis=0) ** 0.5
    if (denom == 0).any():
        raise InputError("One or more criteria columns have all zeros; cannot normalize.")
    norm = X / denom

    weighted = norm * w

    ideal_best = weighted.max(axis=0).copy()
    ideal_worst = weighted.min(axis=0).copy()

    for j, imp in enumerate(impacts):
        if imp == "-":
            ideal_best[j] = weighted[:, j].min()
            ideal_worst[j] = weighted[:, j].max()

    s_pos = ((weighted - ideal_best) ** 2).sum(axis=1) ** 0.5
    s_neg = ((weighted - ideal_worst) ** 2).sum(axis=1) ** 0.5

    denom2 = s_pos + s_neg
    if (denom2 == 0).any():
        raise InputError("Unable to compute TOPSIS score for some rows (division by zero).")

    score = s_neg / denom2

    out = df.copy()
    out["Topsis Score"] = score
    out["Rank"] = out["Topsis Score"].rank(method="dense", ascending=False).astype(int)

    return TopsisResult(out)
