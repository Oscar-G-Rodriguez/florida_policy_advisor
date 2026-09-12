from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

from app.models import AdviceRequest, ForecastItem, Geography

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
HORIZON_MONTHS = {"near_term": 6, "mid_term": 24, "long_term": 60}
SUPPORTED_SECTORS = {"labor_market", "housing", "fiscal"}


@dataclass(frozen=True)
class MetricSpec:
    metric_id: str
    sector: str
    metric: str
    dataset_id: str
    value_col: str
    date_col: str
    unit: str
    preference: str
    series_id: Optional[str] = None


METRICS: List[MetricSpec] = [
    MetricSpec("labor_unemployment_bls", "labor_market", "Unemployment rate (BLS)", "bls_unemployment", "value", "date", "%", "lower_is_better"),
    MetricSpec("labor_unemployment_fred", "labor_market", "Unemployment rate (FRED)", "fred_macro", "value", "date", "%", "lower_is_better", "FLUR"),
    MetricSpec("fiscal_real_gdp", "fiscal", "Real GDP", "fred_macro", "value", "date", "millions of chained dollars", "higher_is_better", "FLNGSP"),
    MetricSpec("housing_median_rent", "housing", "Median gross rent", "census_acs_fl_county", "median_gross_rent", "year", "USD", "lower_is_better"),
    MetricSpec("housing_rent_burden", "housing", "Rent-to-income ratio", "census_acs_fl_county", "rent_to_income", "year", "ratio", "lower_is_better"),
    MetricSpec("housing_vacancy_rate", "housing", "Housing vacancy rate", "census_acs_fl_county", "vacancy_rate", "year", "ratio", "higher_is_better"),
    MetricSpec("housing_home_value", "housing", "Median home value", "census_acs_fl_county", "median_home_value", "year", "USD", "lower_is_better"),
]


def _load_processed(dataset_id: str, filename: str) -> pd.DataFrame:
    path = DATA_DIR / "processed" / dataset_id / filename
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _parse_dates(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series.astype(str), errors="coerce")


def _infer_frequency_months(dates: Iterable[pd.Timestamp]) -> int:
    values = pd.Series(list(dates)).dropna().sort_values()
    if len(values) < 2:
        return 12
    median_days = values.diff().dropna().dt.days.median()
    return 1 if median_days <= 45 else 3 if median_days <= 120 else 12


def _select_acs_geography(df: pd.DataFrame, geography: Geography) -> pd.DataFrame:
    if df.empty:
        return df
    if geography.level == "county":
        if geography.value.isdigit():
            return df[df["county_fips"].astype(str) == geography.value].copy()
        return df[df["county_name"].str.contains(geography.value, case=False, na=False)].copy()
    # A state result is only meaningful when every Florida county is present.
    if df["county_fips"].nunique() < 67:
        return pd.DataFrame()
    columns = ["median_gross_rent", "rent_to_income", "vacancy_rate", "median_home_value"]
    rows = []
    for year, group in df.groupby("year"):
        weights = pd.to_numeric(group.get("population"), errors="coerce").fillna(0)
        row = {"year": year, "county_name": "Florida (population-weighted county estimate)", "county_fips": "12"}
        for column in columns:
            values = pd.to_numeric(group[column], errors="coerce")
            usable = values.notna() & weights.gt(0)
            row[column] = float(np.average(values[usable], weights=weights[usable])) if usable.any() else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def _load_metric_series(spec: MetricSpec, geography: Geography) -> Tuple[pd.DataFrame, List[str]]:
    if spec.dataset_id == "bls_unemployment":
        return _load_processed(spec.dataset_id, "unemployment.csv"), [spec.dataset_id]
    if spec.dataset_id == "fred_macro":
        data = _load_processed(spec.dataset_id, "fred_macro.csv")
        return (data[data["series_id"] == spec.series_id] if spec.series_id and not data.empty else data), [spec.dataset_id]
    return _select_acs_geography(_load_processed(spec.dataset_id, "acs_county.csv"), geography), [spec.dataset_id]


def _temporal_evaluation(values: np.ndarray) -> Tuple[str, Dict[str, float]]:
    """Select a model using chronological one-step holdouts; lower MAE wins."""
    holdout = max(2, min(6, len(values) // 4))
    train_end = len(values) - holdout
    naive_errors: List[float] = []
    linear_errors: List[float] = []
    for index in range(train_end, len(values)):
        train, actual = values[:index], values[index]
        naive_errors.append(abs(actual - train[-1]))
        slope, intercept = np.polyfit(np.arange(len(train)), train, 1)
        linear_errors.append(abs(actual - (slope * len(train) + intercept)))
    naive_mae, linear_mae = float(np.mean(naive_errors)), float(np.mean(linear_errors))
    naive_rmse = float(np.sqrt(np.mean(np.square(naive_errors))))
    linear_rmse = float(np.sqrt(np.mean(np.square(linear_errors))))
    winner = "linear" if linear_mae < naive_mae else "naive"
    return winner, {
        "holdout_points": float(holdout),
        "naive_mae": naive_mae,
        "linear_mae": linear_mae,
        "naive_rmse": naive_rmse,
        "linear_rmse": linear_rmse,
        "selected_mae": linear_mae if winner == "linear" else naive_mae,
        "selected_rmse": linear_rmse if winner == "linear" else naive_rmse,
    }


def _forecast(values: np.ndarray, steps: int, frequency_months: int) -> Tuple[Optional[List[float]], str, str, Optional[float], Dict[str, float]]:
    minimum_points = 12 if frequency_months == 1 else 6
    max_steps = 12 if frequency_months == 1 else 3
    if len(values) < minimum_points:
        return None, "unavailable", f"Needs at least {minimum_points} observations at this frequency; found {len(values)}.", None, {}
    if steps > max_steps:
        return None, "limited", f"Requested {steps} steps exceeds the conservative {max_steps}-step limit for this series.", None, {}
    method, metrics = _temporal_evaluation(values)
    if method == "linear":
        slope, intercept = np.polyfit(np.arange(len(values)), values, 1)
        predictions = [float(slope * (len(values) + step) + intercept) for step in range(1, steps + 1)]
        return predictions, "available", f"Linear trend selected on {metrics['holdout_points']:.0f} chronological holdouts (MAE {metrics['linear_mae']:.3g} vs naïve {metrics['naive_mae']:.3g}).", metrics["selected_mae"], metrics
    return [float(values[-1])] * steps, "available", f"Naïve last-value baseline retained on {metrics['holdout_points']:.0f} chronological holdouts (MAE {metrics['naive_mae']:.3g} vs linear {metrics['linear_mae']:.3g}).", metrics["selected_mae"], metrics


def _classify_direction(predicted: float, baseline: float, preference: str) -> str:
    if abs(predicted - baseline) <= abs(baseline) * 0.02 + 1e-6:
        return "stable"
    if preference == "lower_is_better":
        return "improving" if predicted < baseline else "worsening"
    return "improving" if predicted > baseline else "worsening"


def _format_horizon_label(time_horizon: str) -> str:
    return time_horizon.replace("_", " ")


def _build_outlook_summary(items: List[ForecastItem], issue_area: str) -> str:
    available = [item for item in items if item.status == "available" and (issue_area == "all" or item.sector == issue_area)]
    if not available:
        return "No evaluated forecast is available for this request. Inspect the data-mode notice and refresh or add a longer time series."
    worsening, improving = sum(item.direction == "worsening" for item in available), sum(item.direction == "improving" for item in available)
    if worsening > improving:
        return "The evaluated baseline outlook contains more worsening than improving indicators; it is not a causal policy-impact estimate."
    if improving > worsening:
        return "The evaluated baseline outlook contains more improving than worsening indicators; it is not a causal policy-impact estimate."
    return "The evaluated baseline outlook is mixed; it is not a causal policy-impact estimate."


def _compute_urgency(items: List[ForecastItem]) -> float:
    changes = [min(1.0, abs(item.predicted_value - item.baseline_value) / (abs(item.baseline_value) or 1.0)) for item in items if item.status == "available" and item.direction == "worsening" and item.baseline_value is not None and item.predicted_value is not None]
    return float(np.mean(changes)) if changes else 0.0


def generate_outlook(request: AdviceRequest) -> Tuple[List[ForecastItem], str, float, str]:
    horizon_months = HORIZON_MONTHS[request.time_horizon]
    items: List[ForecastItem] = []
    for spec in METRICS:
        if request.issue_area != "all" and spec.sector != request.issue_area:
            continue
        frame, citations = _load_metric_series(spec, request.geography)
        if frame.empty or spec.value_col not in frame or spec.date_col not in frame:
            items.append(ForecastItem(metric_id=spec.metric_id, sector=spec.sector, metric=spec.metric, horizon=_format_horizon_label(request.time_horizon), unit=spec.unit, direction="unavailable", citations=citations, status="unavailable", method_note="No supported geography-specific data is available."))
            continue
        series = pd.DataFrame({"date": _parse_dates(frame[spec.date_col]), "value": pd.to_numeric(frame[spec.value_col], errors="coerce")}).dropna().sort_values("date").groupby("date", as_index=False)["value"].mean()
        if series.empty:
            continue
        frequency = _infer_frequency_months(series["date"])
        predictions, status, evaluation, uncertainty, validation_metrics = _forecast(series["value"].to_numpy(float), max(1, round(horizon_months / frequency)), frequency)
        baseline = float(series["value"].iloc[-1])
        if predictions is None:
            items.append(ForecastItem(metric_id=spec.metric_id, sector=spec.sector, metric=spec.metric, horizon=_format_horizon_label(request.time_horizon), baseline_value=baseline, unit=spec.unit, direction="unavailable", citations=citations, status=status, method_note=evaluation, validation_metrics=validation_metrics))
            continue
        predicted = predictions[-1]
        items.append(ForecastItem(metric_id=spec.metric_id, sector=spec.sector, metric=spec.metric, horizon=_format_horizon_label(request.time_horizon), predicted_value=predicted, baseline_value=baseline, unit=spec.unit, direction=_classify_direction(predicted, baseline, spec.preference), citations=citations, status="available", method_note="Evaluated univariate baseline; no neural model is used.", evaluation_note=evaluation, uncertainty=uncertainty, validation_metrics=validation_metrics))
    return items, _build_outlook_summary(items, request.issue_area), _compute_urgency(items), "Forecasts use chronological baseline evaluation when minimum-data and horizon rules are met; otherwise they are withheld."
