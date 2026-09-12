from __future__ import annotations

import os
import logging
from datetime import date
from typing import Dict

import pandas as pd
import requests

from app.data.loaders.base import ensure_dir, fixture_path, processed_path, raw_path
from app.data.quality import assess_dataset
from app.data.sqlite import write_table
from app.data.registry import get_dataset_metadata, update_dataset_refresh

CENSUS_BASE = "https://api.census.gov/data"
LOGGER = logging.getLogger(__name__)


def _process_acs_json(data: list) -> pd.DataFrame:
    headers = data[0]
    rows = data[1:]
    df = pd.DataFrame(rows, columns=headers)
    df = df.rename(columns={
        "B19013_001E": "median_household_income",
        "B25064_001E": "median_gross_rent",
        "B17001_002E": "poverty_count",
        "B17001_001E": "population",
        "B01001_001E": "total_population",
        "B25001_001E": "housing_units",
        "B25002_003E": "vacant_units",
        "B25077_001E": "median_home_value",
        "NAME": "county_name",
        "state": "state_fips",
        "county": "county_fips",
    })
    df["median_household_income"] = pd.to_numeric(df["median_household_income"], errors="coerce")
    df["median_gross_rent"] = pd.to_numeric(df["median_gross_rent"], errors="coerce")
    df["poverty_count"] = pd.to_numeric(df["poverty_count"], errors="coerce")
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    df["total_population"] = pd.to_numeric(df["total_population"], errors="coerce")
    df["housing_units"] = pd.to_numeric(df["housing_units"], errors="coerce")
    df["vacant_units"] = pd.to_numeric(df["vacant_units"], errors="coerce")
    df["median_home_value"] = pd.to_numeric(df["median_home_value"], errors="coerce")
    df["poverty_rate"] = (df["poverty_count"] / df["population"]).round(4)
    df["vacancy_rate"] = (df["vacant_units"] / df["housing_units"]).round(4)
    df["rent_to_income"] = (
        (df["median_gross_rent"] * 12) / df["median_household_income"]
    ).round(4)
    df["county_fips"] = df["state_fips"] + df["county_fips"]
    return df[[
        "county_fips",
        "county_name",
        "median_household_income",
        "median_gross_rent",
        "median_home_value",
        "poverty_rate",
        "vacancy_rate",
        "rent_to_income",
        "population",
        "total_population",
        "housing_units",
        "vacant_units",
    ]]


def refresh(allow_network: bool = True) -> Dict[str, str]:
    dataset_id = "census_acs_fl_county"
    years_env = os.getenv("ACS_YEARS")
    if years_env:
        years = [year.strip() for year in years_env.split(",") if year.strip()]
    else:
        years = [str(year) for year in range(2015, 2025)]
    api_key = os.getenv("CENSUS_API_KEY")
    today = date.today()

    processed_file = processed_path(dataset_id, "acs_county.csv")
    ensure_dir(processed_file.parent)
    refresh_error = "No usable rows returned by Census ACS."

    if allow_network and not os.getenv("FORCE_OFFLINE"):
        try:
            variables = [
                "NAME",
                "B19013_001E",
                "B25064_001E",
                "B17001_002E",
                "B17001_001E",
                "B01001_001E",
                "B25001_001E",
                "B25002_003E",
                "B25077_001E",
            ]
            frames = []
            raw_payload = {}
            for year in years:
                params = {
                    "get": ",".join(variables),
                    "for": "county:*",
                    "in": "state:12",
                }
                if api_key:
                    params["key"] = api_key
                url = f"{CENSUS_BASE}/{year}/acs/acs5"
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                raw_payload[year] = response.json()
                df = _process_acs_json(raw_payload[year])
                if not df.empty:
                    df["year"] = int(year)
                    frames.append(df)
            if frames:
                combined = pd.concat(frames, ignore_index=True)
                raw_file = raw_path(dataset_id, "acs.json")
                ensure_dir(raw_file.parent)
                raw_file.write_text(pd.Series(raw_payload).to_json())
                combined.to_csv(processed_file, index=False)
                write_table(combined, dataset_id)
                update_dataset_refresh(dataset_id, today.isoformat(), data_mode="live", quality=assess_dataset(dataset_id, combined))
                return {"dataset_id": dataset_id, "status": "downloaded", "rows": str(len(combined))}
        except requests.RequestException as exc:
            LOGGER.warning("ACS refresh failed; using fixture if available: %s", exc)
            refresh_error = str(exc)
        except (ValueError, KeyError, TypeError) as exc:
            LOGGER.warning("ACS response could not be processed; using fixture if available: %s", exc)
            refresh_error = str(exc)
    else:
        refresh_error = "Network refresh disabled."

    fixture = fixture_path(dataset_id, "acs_county.csv")
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
