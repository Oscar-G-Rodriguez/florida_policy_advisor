# ENV_VARS

This list includes environment variable NAMES only (no values).

## Backend data loaders
- `BLS_API_KEY`: used by `app/data/loaders/bls.py` to authenticate BLS API requests.
- `BLS_SERIES_ID`: used by `app/data/loaders/bls.py` to select the BLS series (default LAUST120000000000003).
- `BLS_START_YEAR`: used by `app/data/loaders/bls.py` to set start year.
- `BLS_END_YEAR`: used by `app/data/loaders/bls.py` to set end year.
- `CENSUS_API_KEY`: used by `app/data/loaders/census_acs.py` for ACS API.
- `ACS_YEAR`: used by `app/data/loaders/census_acs.py` to set a single ACS year (default 2022).
- `ACS_YEARS`: used by `app/data/loaders/census_acs.py` to set multiple ACS years.
- `FRED_API_KEY`: used by `app/data/loaders/fred.py` for FRED API requests.
- `FORCE_OFFLINE`: if set, loaders skip network and use fixtures.

## Forecasting
- `FORECAST_REQUIRE_CUDA`: if set to 1, forecasting fails unless CUDA is available (`app/services/forecast.py`).

## Frontend/API
- `VITE_API_BASE`: frontend API base URL (used in `frontend/src/App.jsx`).
- `VITE_REQUIRE_API`: when `true`, demo mode is disabled (used in `frontend/src/App.jsx`).

## Packaged app
- `APP_HOST`: host for packaged Uvicorn server (`app/packaged.py`).
- `APP_PORT`: port for packaged Uvicorn server (`app/packaged.py`).

## CORS
- `CORS_ORIGINS`: allowed origins (used in `app/main.py`).