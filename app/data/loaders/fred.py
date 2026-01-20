from __future__ import annotations

import os
from datetime import date
from typing import Dict, List

import pandas as pd
import requests

from app.data.loaders.base import ensure_dir, fixture_path, processed_path, raw_path
from app.data.registry import update_dataset_refresh
from app.data.sqlite import write_table

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

SERIES = {
    "FLNGSP": "Florida Real GDP (millions of chained dollars)",
    "FLUR": "Florida Unemployment Rate",
}


def _fetch_series(series_id: str, api_key: str | None) -> List[dict]:
    params = {
        "series_id": series_id,
        "file_type": "json",
    }
    if api_key:
        params["api_key"] = api_key
    response = requests.get(FRED_BASE, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get("observations", [])


def refresh(allow_network: bool = True) -> Dict[str, str]:
    dataset_id = "fred_macro"
    api_key = os.getenv("FRED_API_KEY")
    today = date.today()
    processed_file = processed_path(dataset_id, "fred_macro.csv")
    ensure_dir(processed_file.parent)

    if allow_network and not os.getenv("FORCE_OFFLINE"):
        try:
            rows = []
            raw_payload = {}
            for series_id, series_name in SERIES.items():
                observations = _fetch_series(series_id, api_key)
                raw_payload[series_id] = observations
                for obs in observations[-24:]:
                    value = obs.get("value")
                    if value in (".", None):
                        continue
                    rows.append({
                        "series_id": series_id,
                        "series_name": series_name,
                        "date": obs.get("date"),
                        "value": float(value),
                    })
            raw_file = raw_path(dataset_id, "fred.json")
            ensure_dir(raw_file.parent)
            raw_file.write_text(pd.Series(raw_payload).to_json())
            df = pd.DataFrame(rows)
            if not df.empty:
                df.to_csv(processed_file, index=False)
                write_table(df, dataset_id)
                update_dataset_refresh(dataset_id, today.isoformat())
                return {"dataset_id": dataset_id, "status": "downloaded", "rows": str(len(df))}
        except Exception:
            pass

    fixture = fixture_path(dataset_id, "fred_macro.csv")
    if fixture:
        processed_file.write_text(fixture.read_text())
        raw_file = raw_path(dataset_id, "fixture.csv")
        ensure_dir(raw_file.parent)
        raw_file.write_text(fixture.read_text())
        try:
            df = pd.read_csv(processed_file)
            write_table(df, dataset_id)
        except Exception:
            pass
        update_dataset_refresh(dataset_id, today.isoformat())
        return {"dataset_id": dataset_id, "status": "cached", "rows": "fixture"}

    return {"dataset_id": dataset_id, "status": "failed", "rows": "0"}
