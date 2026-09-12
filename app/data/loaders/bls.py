from __future__ import annotations

import logging
import os
from datetime import date
from pathlib import Path
from typing import Dict

import pandas as pd
import requests

from app.data.loaders.base import ensure_dir, fixture_path, processed_path, raw_path
from app.data.quality import assess_dataset
from app.data.sqlite import write_table
from app.data.registry import get_dataset_metadata, update_dataset_refresh

BLS_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
LOGGER = logging.getLogger(__name__)


def _process_bls_json(payload: Dict) -> pd.DataFrame:
    series = payload.get("Results", {}).get("series", [])
    rows = []
    for series_item in series:
        series_id = series_item.get("seriesID")
        for entry in series_item.get("data", []):
            year = entry.get("year")
            period = entry.get("period", "")
            if not period.startswith("M"):
                continue
            month = period.replace("M", "")
            if not month.isdigit() or not 1 <= int(month) <= 12:
                continue
            date_str = f"{year}-{month.zfill(2)}"
            rows.append({
                "series_id": series_id,
                "date": date_str,
                "value": float(entry.get("value")),
            })
    return pd.DataFrame(rows)


def refresh(allow_network: bool = True) -> Dict[str, str]:
    dataset_id = "bls_unemployment"
    series_id = os.getenv("BLS_SERIES_ID", "LAUST120000000000003")
    start_year = os.getenv("BLS_START_YEAR")
    end_year = os.getenv("BLS_END_YEAR")
    today = date.today()
    start_year = start_year or str(today.year - 2)
    end_year = end_year or str(today.year)

    raw_dir = ensure_dir(raw_path(dataset_id, "").parent)
    processed_file = processed_path(dataset_id, "unemployment.csv")
    ensure_dir(processed_file.parent)
    refresh_error = "No usable rows returned by BLS."

    if allow_network and not os.getenv("FORCE_OFFLINE"):
        try:
            payload = {
                "seriesid": [series_id],
                "startyear": start_year,
                "endyear": end_year,
            }
            api_key = os.getenv("BLS_API_KEY")
            if api_key:
                payload["registrationkey"] = api_key
            response = requests.post(BLS_URL, json=payload, timeout=30)
            response.raise_for_status()
            raw_file = raw_path(dataset_id, "bls.json")
            raw_file.write_text(response.text)
            df = _process_bls_json(response.json())
            if not df.empty:
                df.to_csv(processed_file, index=False)
                write_table(df, dataset_id)
                update_dataset_refresh(dataset_id, today.isoformat(), data_mode="live", quality=assess_dataset(dataset_id, df))
                return {"dataset_id": dataset_id, "status": "downloaded", "rows": str(len(df))}
        except requests.RequestException as exc:
            LOGGER.warning("BLS refresh failed; using fixture if available: %s", exc)
            refresh_error = str(exc)
        except (ValueError, KeyError, TypeError) as exc:
            LOGGER.warning("BLS response could not be processed; using fixture if available: %s", exc)
            refresh_error = str(exc)
    else:
        refresh_error = "Network refresh disabled."

    fixture = fixture_path(dataset_id, "unemployment.csv")
    if fixture:
        processed_file.write_text(fixture.read_text())
        raw_file = raw_path(dataset_id, "fixture.csv")
        ensure_dir(raw_file.parent)
        raw_file.write_text(fixture.read_text())
        df = pd.read_csv(processed_file)
        write_table(df, dataset_id)
        update_dataset_refresh(dataset_id, get_dataset_metadata(dataset_id)["retrieval_date"], data_mode="fixture", last_error=refresh_error, quality=assess_dataset(dataset_id, df))
        return {"dataset_id": dataset_id, "status": "fixture", "rows": str(len(df)), "error": refresh_error}

    return {"dataset_id": dataset_id, "status": "failed", "rows": "0"}
