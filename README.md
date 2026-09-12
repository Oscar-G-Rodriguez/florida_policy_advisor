# Florida Policy Advisor

Florida Policy Advisor is a local Windows application for exploring a narrow, traceable set of Florida policy indicators and heuristic policy options. The application was authored by its developer for the Congressional App Challenge, then withdrawn before submission for personal reasons. It was not submitted, judged, placed, or externally validated by the competition.

## What works today

- **Supported live sectors:** labor market (BLS and FRED unemployment), housing (Census ACS county indicators), and fiscal outlook (FRED Florida real GDP).
- **Clear provenance:** every result identifies `live`, `fixture`, `mixed`, or `unknown` data. The bundled fixture is visibly marked as offline sample data and is never described as current analysis.
- **Traceable outputs:** numeric evidence and forecasts link to a dataset ID, source URL, and retrieval date. Memos carry the same citations and source-mode notice.
- **Data-quality evidence:** each refresh records row counts, schema fingerprint, required-field null rates, duplicate-key rows, invalid-value rows, date coverage, and per-series coverage.
- **Conservative forecasts:** the application uses only naïve-last-value and linear-trend baselines, selected using chronological holdouts with MAE and RMSE. Forecasts are withheld when the time series is too short or the requested horizon is too long.
- **Heuristic policy ranking:** options and bundles are transparent prioritization aids. They are not estimates of causal policy effects, and the configured impact weights are not empirical effect sizes.

Other sectors in the historical registry are intentionally shown as unavailable. They do not have active loaders or supported end-to-end analysis paths.

## Run locally

Prerequisites: Python 3.11+ and Node.js 18+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd frontend
npm ci
cd ..
.\scripts\dev.ps1
```

Open `http://127.0.0.1:5173`. The development UI calls the backend by default. It does not silently fall back to hard-coded output. To build an explicitly labeled visual demo only, set `VITE_DEMO_MODE=true` before building the frontend.

## Data modes and refresh

The repository includes small deterministic fixtures for tests and offline demonstrations. They are not live data. Refresh supported sources with:

```powershell
.\scripts\refresh_data.ps1
```

Use `POST /api/refresh?offline=true` to deliberately restore offline fixtures without calling external APIs. Live refreshes write raw responses under `data/raw/` (git-ignored) and update the source mode and retrieval date in `data/registry_state.json`.

Structural quality and freshness are separate: a dataset can pass schema, null, duplicate, and value checks while still being stale or fixture-backed. `source_age_days`, source mode, and retrieval date make that distinction explicit.

Optional environment variables:

```text
BLS_API_KEY=optional_bls_key
CENSUS_API_KEY=optional_census_key
FRED_API_KEY=required_for_live_fred_refresh
ACS_YEARS=2020,2021,2022,2023,2024
CORS_ORIGINS=http://localhost:5173
```

## Verify

```powershell
pytest -q
cd frontend
npm run build
```

Generate a reproducible data-quality artifact:

```powershell
python .\scripts\validate_data.py
python .\scripts\report_forecast_validation.py
```

The backend test suite is offline and fixture-backed. See [docs/VALIDATION.md](docs/VALIDATION.md) and [portfolio evidence](portfolio_evidence/README.md) for the exact checks, expected baseline behavior, sample API request, quality and forecast-validation artifacts, and browser smoke-test checklist.

## Package for Windows

```powershell
.\scripts\build_single_app.ps1
```

The packaged desktop app serves the compiled frontend from its bundled FastAPI backend. It therefore follows the API path by default; it does not select frontend demo mode. Install Microsoft Edge WebView2 if the desktop window cannot render.

## Project map

- [Architecture and data flow](docs/ARCHITECTURE.md)
- [Validation report and demo checklist](docs/VALIDATION.md)
- `app/data/loaders/`: BLS, ACS, and FRED loaders
- `app/services/forecast.py`: evaluated baseline forecasting rules
- `app/core/citations.py`: citation and response guardrails
- `app/services/memo.py`: cited memo export

## Limitations

The tool is an educational prototype, not a decision system. Its fixture dataset is deliberately small; it produces no forecast from it. Even with live data, the forecasts are univariate statistical baselines and should not be used to infer causality or select policy without subject-matter review. ACS state output is only produced when all 67 Florida counties are present; county results remain county-specific.
