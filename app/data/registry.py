from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class DatasetDefinition:
    dataset_id: str
    name: str
    description: str
    url: str
    license: str
    refresh_method: str


DATASETS: Dict[str, DatasetDefinition] = {
    "bls_unemployment": DatasetDefinition(
        dataset_id="bls_unemployment",
        name="BLS State Unemployment Rate (Florida)",
        description="Monthly unemployment rate for Florida from the BLS public API.",
        url="https://api.bls.gov/publicAPI/v2/timeseries/data/",
        license="Public domain",
        refresh_method="HTTP API",
    ),
    "census_acs_fl_county": DatasetDefinition(
        dataset_id="census_acs_fl_county",
        name="Census ACS 5-year Florida County Indicators",
        description="County-level income, rent, and poverty estimates for Florida.",
        url="https://api.census.gov/data.html",
        license="Public domain",
        refresh_method="HTTP API",
    ),
    "fred_macro": DatasetDefinition(
        dataset_id="fred_macro",
        name="FRED Florida Macro Series",
        description="Selected Florida macroeconomic series from FRED.",
        url="https://api.stlouisfed.org/fred/",
        license="FRED Terms of Use",
        refresh_method="HTTP API",
    ),
    "nces_ccd_grad": DatasetDefinition(
        dataset_id="nces_ccd_grad",
        name="NCES CCD Graduation Rates",
        description="State graduation and completion statistics from NCES CCD.",
        url="https://nces.ed.gov/ccd/",
        license="Public domain",
        refresh_method="Download",
    ),
    "cdc_places": DatasetDefinition(
        dataset_id="cdc_places",
        name="CDC PLACES Health Indicators",
        description="County-level chronic disease and risk factor indicators.",
        url="https://www.cdc.gov/places/",
        license="Public domain",
        refresh_method="Download",
    ),
    "fema_nri": DatasetDefinition(
        dataset_id="fema_nri",
        name="FEMA National Risk Index",
        description="Hazard risk index and expected annual loss indicators.",
        url="https://hazards.fema.gov/nri/",
        license="Public domain",
        refresh_method="Download",
    ),
    "fhwa_hpms": DatasetDefinition(
        dataset_id="fhwa_hpms",
        name="FHWA Highway Performance Monitoring System",
        description="Transportation condition and performance indicators.",
        url="https://highways.dot.gov/safety/data-analysis-tools/rsdp/rsdp-tools/highway-performance-monitoring-system-hpms",
        license="Public domain",
        refresh_method="Download",
    ),
    "epa_air": DatasetDefinition(
        dataset_id="epa_air",
        name="EPA Air Quality (AQS)",
        description="Air quality monitoring and PM2.5 indicators.",
        url="https://www.epa.gov/air-data",
        license="Public domain",
        refresh_method="HTTP API",
    ),
    "fbi_ucr": DatasetDefinition(
        dataset_id="fbi_ucr",
        name="FBI Crime Data Explorer",
        description="Crime rates and offense statistics.",
        url="https://cde.ucr.cjis.gov/",
        license="Public domain",
        refresh_method="HTTP API",
    ),
    "eia_energy": DatasetDefinition(
        dataset_id="eia_energy",
        name="EIA State Energy Data",
        description="Energy prices and consumption by sector.",
        url="https://www.eia.gov/opendata/",
        license="Public domain",
        refresh_method="HTTP API",
    ),
    "fcc_bdc": DatasetDefinition(
        dataset_id="fcc_bdc",
        name="FCC Broadband Data Collection",
        description="Broadband availability and coverage statistics.",
        url="https://broadbandmap.fcc.gov/",
        license="Public domain",
        refresh_method="Download",
    ),
    "census_popest": DatasetDefinition(
        dataset_id="census_popest",
        name="Census Population Estimates",
        description="Annual population and migration estimates.",
        url="https://www.census.gov/data/developers/data-sets/popest-popproj/popest.html",
        license="Public domain",
        refresh_method="HTTP API",
    ),
    "census_bds": DatasetDefinition(
        dataset_id="census_bds",
        name="Census Business Dynamics Statistics",
        description="Firm births, deaths, and startup rates.",
        url="https://www.census.gov/programs-surveys/bds/data.API.html",
        license="Public domain",
        refresh_method="HTTP API",
    ),
    "usda_nass": DatasetDefinition(
        dataset_id="usda_nass",
        name="USDA NASS QuickStats",
        description="Agricultural production and yield indicators.",
        url="https://quickstats.nass.usda.gov/",
        license="Public domain",
        refresh_method="HTTP API",
    ),
}

ROOT_DIR = Path(__file__).resolve().parents[2]
REGISTRY_STATE_PATH = ROOT_DIR / "data" / "registry_state.json"


def _default_state() -> Dict[str, Dict[str, str]]:
    today = date.today().isoformat()
    return {
        dataset_id: {
            "retrieval_date": today,
            "last_refresh": today,
        }
        for dataset_id in DATASETS
    }


def _load_state() -> Dict[str, Dict[str, str]]:
    if not REGISTRY_STATE_PATH.exists():
        state = _default_state()
        REGISTRY_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        REGISTRY_STATE_PATH.write_text(json.dumps(state, indent=2))
        return state
    return json.loads(REGISTRY_STATE_PATH.read_text())


def _save_state(state: Dict[str, Dict[str, str]]) -> None:
    REGISTRY_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_STATE_PATH.write_text(json.dumps(state, indent=2))


def list_datasets() -> List[Dict[str, str]]:
    state = _load_state()
    datasets = []
    for dataset_id, definition in DATASETS.items():
        dataset_state = state.get(dataset_id, {})
        datasets.append({
            **asdict(definition),
            "retrieval_date": dataset_state.get("retrieval_date", "unknown"),
            "last_refresh": dataset_state.get("last_refresh", "unknown"),
        })
    return datasets


def update_dataset_refresh(dataset_id: str, retrieval_date: str) -> None:
    state = _load_state()
    state.setdefault(dataset_id, {})
    state[dataset_id]["retrieval_date"] = retrieval_date
    state[dataset_id]["last_refresh"] = date.today().isoformat()
    _save_state(state)


def get_dataset_metadata(dataset_id: str) -> Dict[str, str]:
    definition = DATASETS[dataset_id]
    state = _load_state().get(dataset_id, {})
    return {
        **asdict(definition),
        "retrieval_date": state.get("retrieval_date", "unknown"),
    }
