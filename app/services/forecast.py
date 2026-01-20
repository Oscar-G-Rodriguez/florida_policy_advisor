from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

from app.models import AdviceRequest, ForecastItem, Geography

try:
    import torch
except ImportError:  # pragma: no cover - optional GPU dependency
    torch = None

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"

HORIZON_MONTHS = {
    "near_term": 6,
    "mid_term": 24,
    "long_term": 60,
}


@dataclass(frozen=True)
class MetricSpec:
    metric_id: str
    sector: str
    metric: str
    dataset_id: str
    source: str
    value_col: str
    date_col: str
    unit: str
    preference: str
    series_id: Optional[str] = None


METRICS: List[MetricSpec] = [
    MetricSpec(
        metric_id="labor_unemployment_bls",
        sector="labor_market",
        metric="Unemployment rate (BLS)",
        dataset_id="bls_unemployment",
        source="bls",
        value_col="value",
        date_col="date",
        unit="%",
        preference="lower_is_better",
    ),
    MetricSpec(
        metric_id="labor_unemployment_fred",
        sector="labor_market",
        metric="Unemployment rate (FRED)",
        dataset_id="fred_macro",
        source="fred",
        value_col="value",
        date_col="date",
        unit="%",
        preference="lower_is_better",
        series_id="FLUR",
    ),
    MetricSpec(
        metric_id="fiscal_real_gdp",
        sector="fiscal",
        metric="Real GDP",
        dataset_id="fred_macro",
        source="fred",
        value_col="value",
        date_col="date",
        unit="USD",
        preference="higher_is_better",
        series_id="FLNGSP",
    ),
    MetricSpec(
        metric_id="housing_median_rent",
        sector="housing",
        metric="Median gross rent",
        dataset_id="census_acs_fl_county",
        source="acs",
        value_col="median_gross_rent",
        date_col="year",
        unit="USD",
        preference="lower_is_better",
    ),
    MetricSpec(
        metric_id="housing_rent_burden",
        sector="housing",
        metric="Rent-to-income ratio",
        dataset_id="census_acs_fl_county",
        source="acs",
        value_col="rent_to_income",
        date_col="year",
        unit="ratio",
        preference="lower_is_better",
    ),
    MetricSpec(
        metric_id="housing_vacancy_rate",
        sector="housing",
        metric="Housing vacancy rate",
        dataset_id="census_acs_fl_county",
        source="acs",
        value_col="vacancy_rate",
        date_col="year",
        unit="ratio",
        preference="higher_is_better",
    ),
    MetricSpec(
        metric_id="housing_home_value",
        sector="housing",
        metric="Median home value",
        dataset_id="census_acs_fl_county",
        source="acs",
        value_col="median_home_value",
        date_col="year",
        unit="USD",
        preference="lower_is_better",
    ),
    MetricSpec(
        metric_id="general_population",
        sector="general",
        metric="Population",
        dataset_id="census_acs_fl_county",
        source="acs",
        value_col="population",
        date_col="year",
        unit="count",
        preference="higher_is_better",
    ),
    MetricSpec(
        metric_id="education_grad_rate",
        sector="education",
        metric="High school graduation rate",
        dataset_id="nces_ccd_grad",
        source="nces",
        value_col="graduation_rate",
        date_col="year",
        unit="%",
        preference="higher_is_better",
    ),
    MetricSpec(
        metric_id="health_chronic_rate",
        sector="health",
        metric="Chronic disease prevalence",
        dataset_id="cdc_places",
        source="cdc",
        value_col="prevalence_rate",
        date_col="year",
        unit="%",
        preference="lower_is_better",
    ),
    MetricSpec(
        metric_id="climate_risk_index",
        sector="climate",
        metric="FEMA National Risk Index",
        dataset_id="fema_nri",
        source="fema",
        value_col="risk_index",
        date_col="year",
        unit="index",
        preference="lower_is_better",
    ),
    MetricSpec(
        metric_id="infrastructure_road_condition",
        sector="infrastructure",
        metric="Road condition index",
        dataset_id="fhwa_hpms",
        source="fhwa",
        value_col="condition_index",
        date_col="year",
        unit="index",
        preference="higher_is_better",
    ),
    MetricSpec(
        metric_id="environment_pm25",
        sector="environment",
        metric="PM2.5 concentration",
        dataset_id="epa_air",
        source="epa",
        value_col="pm25",
        date_col="date",
        unit="ug/m3",
        preference="lower_is_better",
    ),
    MetricSpec(
        metric_id="public_safety_violent_crime",
        sector="public_safety",
        metric="Violent crime rate",
        dataset_id="fbi_ucr",
        source="fbi",
        value_col="violent_crime_rate",
        date_col="year",
        unit="per_100k",
        preference="lower_is_better",
    ),
    MetricSpec(
        metric_id="energy_retail_price",
        sector="energy",
        metric="Retail electricity price",
        dataset_id="eia_energy",
        source="eia",
        value_col="price_cents_kwh",
        date_col="date",
        unit="cents/kwh",
        preference="lower_is_better",
    ),
    MetricSpec(
        metric_id="broadband_access",
        sector="broadband",
        metric="Broadband availability",
        dataset_id="fcc_bdc",
        source="fcc",
        value_col="served_pct",
        date_col="year",
        unit="%",
        preference="higher_is_better",
    ),
    MetricSpec(
        metric_id="demographics_net_migration",
        sector="demographics",
        metric="Net migration",
        dataset_id="census_popest",
        source="census",
        value_col="net_migration",
        date_col="year",
        unit="count",
        preference="higher_is_better",
    ),
    MetricSpec(
        metric_id="business_startup_rate",
        sector="business_dynamism",
        metric="Startup rate",
        dataset_id="census_bds",
        source="census",
        value_col="startup_rate",
        date_col="year",
        unit="%",
        preference="higher_is_better",
    ),
    MetricSpec(
        metric_id="agriculture_yield",
        sector="agriculture",
        metric="Crop yield index",
        dataset_id="usda_nass",
        source="usda",
        value_col="yield_index",
        date_col="year",
        unit="index",
        preference="higher_is_better",
    ),
]


def _load_processed(dataset_id: str, filename: str) -> pd.DataFrame:
    processed_path = DATA_DIR / "processed" / dataset_id / filename
    if processed_path.exists():
        return pd.read_csv(processed_path)
    return pd.DataFrame()


def _parse_dates(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def _to_monthly_series(df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
    dates = _parse_dates(df[date_col])
    values = pd.to_numeric(df[value_col], errors="coerce")
    series = pd.DataFrame({"date": dates, "value": values}).dropna()
    if series.empty:
        return series
    series = series.sort_values("date").set_index("date")
    series = series.resample("MS").mean()
    series["value"] = series["value"].ffill()
    return series.reset_index()


def _infer_frequency_months(dates: Iterable[pd.Timestamp]) -> int:
    dates = pd.Series(list(dates)).dropna().sort_values()
    if len(dates) < 2:
        return 12
    deltas = dates.diff().dropna().dt.days
    if deltas.empty:
        return 12
    median_days = deltas.median()
    if median_days <= 45:
        return 1
    if median_days <= 120:
        return 3
    return 12


def _window_data(values: np.ndarray, lookback: int) -> Tuple[np.ndarray, np.ndarray]:
    xs = []
    ys = []
    for i in range(len(values) - lookback):
        xs.append(values[i : i + lookback])
        ys.append(values[i + lookback])
    return np.array(xs, dtype=np.float32), np.array(ys, dtype=np.float32)


def _forecast_with_torch(values: np.ndarray, steps: int) -> Tuple[List[float], str]:
    if torch is None:
        raise RuntimeError("Torch is not available.")
    require_cuda = os.getenv("FORECAST_REQUIRE_CUDA") == "1"
    has_cuda = torch.cuda.is_available()
    if require_cuda and not has_cuda:
        raise RuntimeError("CUDA required but not available.")
    device = torch.device("cuda" if has_cuda else "cpu")
    lookback = min(6, max(2, len(values) - 1))
    x, y = _window_data(values, lookback)
    if len(x) == 0:
        return [], "Insufficient data for forecasting"

    torch.manual_seed(42)
    model = torch.nn.Sequential(
        torch.nn.Linear(lookback, 16),
        torch.nn.ReLU(),
        torch.nn.Linear(16, 1),
    ).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = torch.nn.MSELoss()
    x_tensor = torch.tensor(x, device=device)
    y_tensor = torch.tensor(y, device=device).unsqueeze(-1)

    for _ in range(200):
        optimizer.zero_grad()
        preds = model(x_tensor)
        loss = loss_fn(preds, y_tensor)
        loss.backward()
        optimizer.step()

    history = list(values.astype(np.float32))
    predictions = []
    model.eval()
    for _ in range(steps):
        window = np.array(history[-lookback:], dtype=np.float32)
        window_tensor = torch.tensor(window, device=device).unsqueeze(0)
        with torch.no_grad():
            pred = model(window_tensor).cpu().numpy().flatten()[0]
        history.append(pred)
        predictions.append(float(pred))

    return predictions, f"Torch MLP ({device.type})"


def _forecast_with_linear(values: np.ndarray, steps: int) -> Tuple[List[float], str]:
    x = np.arange(len(values))
    coeffs = np.polyfit(x, values, 1)
    predictions = []
    for i in range(1, steps + 1):
        predictions.append(float(coeffs[0] * (len(values) + i) + coeffs[1]))
    return predictions, "Numpy linear fallback"


def _forecast_series(values: np.ndarray, steps: int) -> Tuple[List[float], str]:
    require_cuda = os.getenv("FORECAST_REQUIRE_CUDA") == "1"
    if torch is not None:
        try:
            return _forecast_with_torch(values, steps)
        except Exception:
            if require_cuda:
                raise
    elif require_cuda:
        raise RuntimeError("CUDA required but torch is not installed.")
    return _forecast_with_linear(values, steps)


def _standardize(values: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = values.mean(axis=0)
    std = values.std(axis=0)
    std = np.where(std < 1e-6, 1.0, std)
    return (values - mean) / std, mean, std


def _forecast_multifactor(df: pd.DataFrame, steps: int) -> Tuple[Dict[str, List[float]], str]:
    require_cuda = os.getenv("FORECAST_REQUIRE_CUDA") == "1"
    if torch is None:
        if require_cuda:
            raise RuntimeError("CUDA required but torch is not installed.")
        return {}, "Torch not available for multifactor model"

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if require_cuda and device.type != "cuda":
        raise RuntimeError("CUDA required but not available.")

    feature_cols = [col for col in df.columns if col != "date"]
    data = df[feature_cols].to_numpy(dtype=np.float32)
    if len(data) < 4 or len(feature_cols) < 3:
        return {}, "Insufficient data for multifactor model"

    x_raw = data[:-1]
    y_raw = data[1:]
    x_scaled, mean, std = _standardize(x_raw)
    y_scaled = (y_raw - mean) / std

    torch.manual_seed(42)
    x_tensor = torch.tensor(x_scaled, device=device)
    y_tensor = torch.tensor(y_scaled, device=device)

    model = torch.nn.Sequential(
        torch.nn.Linear(len(feature_cols), 32),
        torch.nn.ReLU(),
        torch.nn.Linear(32, len(feature_cols)),
    ).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = torch.nn.MSELoss()

    for _ in range(250):
        optimizer.zero_grad()
        preds = model(x_tensor)
        loss = loss_fn(preds, y_tensor)
        loss.backward()
        optimizer.step()

    current = data[-1].astype(np.float32)
    forecasts: Dict[str, List[float]] = {col: [] for col in feature_cols}
    model.eval()
    for _ in range(steps):
        current_scaled = (current - mean) / std
        input_tensor = torch.tensor(current_scaled, device=device).unsqueeze(0)
        with torch.no_grad():
            next_scaled = model(input_tensor).cpu().numpy().flatten()
        next_values = next_scaled * std + mean
        for idx, col in enumerate(feature_cols):
            forecasts[col].append(float(next_values[idx]))
        current = next_values.astype(np.float32)

    return forecasts, f"Multifactor MLP ({device.type})"


def _select_acs_geography(df: pd.DataFrame, geography: Geography) -> pd.DataFrame:
    if df.empty:
        return df
    if geography.level == "county":
        if geography.value.isdigit():
            match = df[df["county_fips"] == geography.value]
            if not match.empty:
                return match
        match = df[df["county_name"].str.contains(geography.value, case=False, na=False)]
        if not match.empty:
            return match
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if "year" in numeric_cols:
        numeric_cols = numeric_cols.drop("year")
    grouped = df.groupby("year")[numeric_cols].mean().reset_index()
    grouped["county_name"] = "Florida (avg)"
    grouped["county_fips"] = "state"
    return grouped


def _load_metric_series(spec: MetricSpec, geography: Geography) -> Tuple[pd.DataFrame, List[str]]:
    if spec.dataset_id == "bls_unemployment":
        df = _load_processed("bls_unemployment", "unemployment.csv")
        if spec.series_id:
            df = df[df["series_id"] == spec.series_id]
        elif "series_id" in df.columns and not df.empty:
            df = df[df["series_id"] == df["series_id"].iloc[0]]
        return df, ["bls_unemployment"]

    if spec.dataset_id == "fred_macro":
        df = _load_processed("fred_macro", "fred_macro.csv")
        if spec.series_id:
            df = df[df["series_id"] == spec.series_id]
        return df, ["fred_macro"]

    if spec.dataset_id == "census_acs_fl_county":
        df = _load_processed("census_acs_fl_county", "acs_county.csv")
        if "year" not in df.columns:
            return pd.DataFrame(), ["census_acs_fl_county"]
        df = _select_acs_geography(df, geography)
        return df, ["census_acs_fl_county"]

    generic_by_metric = DATA_DIR / "processed" / spec.dataset_id / f"{spec.metric_id}.csv"
    if generic_by_metric.exists():
        return pd.read_csv(generic_by_metric), [spec.dataset_id]
    generic = DATA_DIR / "processed" / spec.dataset_id / "metrics.csv"
    if generic.exists():
        return pd.read_csv(generic), [spec.dataset_id]

    return pd.DataFrame(), []


def _build_feature_table(request: AdviceRequest) -> Tuple[pd.DataFrame, Dict[str, MetricSpec], Dict[str, List[str]]]:
    frames: List[pd.DataFrame] = []
    specs: Dict[str, MetricSpec] = {}
    citations: Dict[str, List[str]] = {}

    for spec in METRICS:
        df, metric_citations = _load_metric_series(spec, request.geography)
        if df.empty or spec.value_col not in df.columns:
            continue
        monthly = _to_monthly_series(df, spec.date_col, spec.value_col)
        if monthly.empty or len(monthly) < 3:
            continue
        series = monthly.rename(columns={"value": spec.metric_id})
        frames.append(series)
        specs[spec.metric_id] = spec
        citations[spec.metric_id] = metric_citations

    if not frames:
        return pd.DataFrame(), {}, {}

    combined = frames[0]
    for frame in frames[1:]:
        combined = combined.merge(frame, on="date", how="outer")

    combined = combined.sort_values("date").set_index("date")
    valid_cols = [
        col for col in combined.columns
        if combined[col].notna().sum() >= 3
    ]
    combined = combined[valid_cols].ffill()
    combined = combined.dropna(axis=0, how="any")
    combined = combined.reset_index()
    specs = {metric_id: spec for metric_id, spec in specs.items() if metric_id in valid_cols}
    citations = {metric_id: cites for metric_id, cites in citations.items() if metric_id in valid_cols}
    return combined, specs, citations


def _classify_direction(predicted: float, baseline: Optional[float], preference: str) -> str:
    if baseline is None:
        return "unclear"
    delta = predicted - baseline
    if abs(delta) <= (abs(baseline) * 0.02 + 1e-6):
        return "stable"
    if preference == "higher_is_better":
        return "improving" if delta > 0 else "worsening"
    if preference == "lower_is_better":
        return "improving" if delta < 0 else "worsening"
    return "mixed"


def _format_horizon_label(time_horizon: str) -> str:
    return time_horizon.replace("_", " ")


def _build_outlook_summary(items: List[ForecastItem], issue_area: str) -> str:
    if issue_area == "all":
        relevant = items
    else:
        relevant = [item for item in items if item.sector == issue_area]
    if not relevant:
        return "Outlook coverage is limited; add more sector indicators to expand foresight."
    worsening = sum(1 for item in relevant if item.direction == "worsening")
    improving = sum(1 for item in relevant if item.direction == "improving")
    if worsening > improving:
        return "Outlook suggests rising pressure in the selected sector over the chosen horizon."
    if improving > worsening:
        return "Outlook suggests conditions could improve in the selected sector over the chosen horizon."
    return "Outlook is mixed, suggesting both opportunities and risks ahead."


def _compute_urgency(items: List[ForecastItem]) -> float:
    worsening = [item for item in items if item.direction == "worsening"]
    if not worsening:
        return 0.0
    scores = []
    for item in worsening:
        if item.baseline_value is None:
            continue
        scale = abs(item.baseline_value) or 1.0
        change = abs(item.predicted_value - item.baseline_value) / scale
        scores.append(min(1.0, change))
    if not scores:
        return 0.0
    return min(1.0, float(np.mean(scores)))


def generate_outlook(request: AdviceRequest) -> Tuple[List[ForecastItem], str, float, str]:
    horizon_months = HORIZON_MONTHS.get(request.time_horizon, 12)
    items: List[ForecastItem] = []
    model_notes: List[str] = []

    feature_table, specs, citations_map = _build_feature_table(request)
    multifactor_predictions: Dict[str, List[float]] = {}
    multifactor_note = ""
    if not feature_table.empty and len(feature_table) >= 4 and len(specs) >= 3:
        multifactor_predictions, multifactor_note = _forecast_multifactor(feature_table, horizon_months)
        if multifactor_predictions:
            model_notes.append(multifactor_note)

    for spec in METRICS:
        df, citations = _load_metric_series(spec, request.geography)
        if df.empty or spec.value_col not in df.columns:
            continue
        dates = _parse_dates(df[spec.date_col])
        values = pd.to_numeric(df[spec.value_col], errors="coerce")
        series = pd.DataFrame({"date": dates, "value": values}).dropna()
        series = series.sort_values("date")
        if len(series) < 3:
            continue
        baseline_value = float(series["value"].iloc[-1])
        if spec.metric_id in multifactor_predictions:
            predictions = multifactor_predictions[spec.metric_id]
            predicted_value = predictions[-1]
            model_note = multifactor_note
            metric_citations = citations_map.get(spec.metric_id, citations)
        else:
            freq_months = _infer_frequency_months(series["date"])
            steps = max(1, int(round(horizon_months / freq_months)))
            predictions, model_note = _forecast_series(series["value"].to_numpy(dtype=np.float32), steps)
            if not predictions:
                continue
            predicted_value = predictions[-1]
            metric_citations = citations
            if model_note not in model_notes:
                model_notes.append(model_note)

        direction = _classify_direction(predicted_value, baseline_value, spec.preference)
        items.append(ForecastItem(
            metric_id=spec.metric_id,
            sector=spec.sector,
            metric=spec.metric,
            horizon=_format_horizon_label(request.time_horizon),
            predicted_value=predicted_value,
            baseline_value=baseline_value,
            unit=spec.unit,
            direction=direction,
            citations=metric_citations,
            method_note=model_note,
        ))

    summary = _build_outlook_summary(items, request.issue_area)
    if request.issue_area == "all":
        urgency = _compute_urgency(items)
    else:
        urgency = _compute_urgency([item for item in items if item.sector == request.issue_area])
    forecast_info = " / ".join(model_notes) if model_notes else "No forecast model available"
    return items, summary, urgency, forecast_info
