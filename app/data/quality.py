from __future__ import annotations

import hashlib
from typing import Any, Dict

import pandas as pd


RULES: Dict[str, Dict[str, object]] = {
    "bls_unemployment": {
        "required": ["series_id", "date", "value"],
        "key": ["series_id", "date"],
        "date": "date",
        "non_negative": ["value"],
        "bounded": {"value": (0, 100)},
    },
    "fred_macro": {
        "required": ["series_id", "date", "value"],
        "key": ["series_id", "date"],
        "date": "date",
        "non_negative": ["value"],
    },
    "census_acs_fl_county": {
        "required": ["county_fips", "county_name", "year", "median_household_income", "median_gross_rent"],
        "key": ["county_fips", "year"],
        "date": "year",
        "non_negative": ["median_household_income", "median_gross_rent", "median_home_value", "population"],
        "bounded": {"poverty_rate": (0, 1), "vacancy_rate": (0, 1), "rent_to_income": (0, 1)},
    },
}


def assess_dataset(dataset_id: str, frame: pd.DataFrame) -> Dict[str, Any]:
    """Return compact, serializable checks without silently repairing source data."""
    rules = RULES.get(dataset_id, {})
    required = list(rules.get("required", []))
    missing_columns = [column for column in required if column not in frame.columns]
    report: Dict[str, Any] = {
        "dataset_id": dataset_id,
        "row_count": int(len(frame)),
        "column_count": int(len(frame.columns)),
        "missing_columns": missing_columns,
        "required_null_rates": {},
        "duplicate_key_rows": 0,
        "invalid_value_rows": 0,
        "date_range": None,
        "series_counts": {},
        "schema_fingerprint": hashlib.sha256("|".join(map(str, frame.columns)).encode("utf-8")).hexdigest()[:12],
    }
    if frame.empty or missing_columns:
        report["status"] = "fail"
        return report

    report["required_null_rates"] = {
        column: round(float(frame[column].isna().mean()), 6) for column in required
    }
    key = list(rules.get("key", []))
    if key:
        report["duplicate_key_rows"] = int(frame.duplicated(key, keep=False).sum())

    invalid = pd.Series(False, index=frame.index)
    for column in rules.get("non_negative", []):
        if column in frame:
            invalid |= pd.to_numeric(frame[column], errors="coerce").lt(0).fillna(False)
    for column, bounds in dict(rules.get("bounded", {})).items():
        if column in frame:
            values = pd.to_numeric(frame[column], errors="coerce")
            invalid |= (values.lt(bounds[0]) | values.gt(bounds[1])).fillna(False)
    report["invalid_value_rows"] = int(invalid.sum())

    date_column = rules.get("date")
    if date_column and date_column in frame:
        dates = pd.to_datetime(frame[date_column].astype(str), errors="coerce").dropna()
        if not dates.empty:
            report["date_range"] = {"start": dates.min().date().isoformat(), "end": dates.max().date().isoformat()}
    if "series_id" in frame:
        report["series_counts"] = {str(key): int(value) for key, value in frame.groupby("series_id").size().items()}

    has_nulls = any(rate > 0 for rate in report["required_null_rates"].values())
    report["status"] = "fail" if report["duplicate_key_rows"] or report["invalid_value_rows"] else "warning" if has_nulls else "pass"
    return report
