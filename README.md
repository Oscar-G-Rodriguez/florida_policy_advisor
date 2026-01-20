# Florida Policy Advisor (MVP)

Local-first MVP that generates evidence-backed policy options with a selectable policy lens. Designed for Windows and non-technical users.

## Requirements
- Python 3.11+
- Node.js 18+

## Setup (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd frontend
npm install
cd ..
```

## Run (one command)
```powershell
.\scripts\dev.ps1
```

- Backend: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:5173

## Frontend-only (no backend)
```powershell
cd frontend
npm install
npm run dev
```
The UI will default to Demo mode if no API base is set. To point at a deployed API:
```powershell
$env:VITE_API_BASE="https://your-api.example.com"
npm run dev
```

## Single-install build (Windows)
This bundles the backend + built frontend into one executable.
```powershell
.\scripts\build_single_app.ps1
```
The executable is created at `dist\FloridaPolicyAdvisor.exe`.

## Two-click installer build (Windows)
- Double-click `BuildApp.cmd` (or run `.\scripts\build_installer.ps1`)
- If Inno Setup is missing, the script will install it via winget.
The installer is created at `dist\FloridaPolicyAdvisor-Setup.exe`.

## Holistic mode
- Choose "All sectors (holistic)" to generate multi-sector outlooks.
- Set `objective_mode` globally (improve/stabilize/resilience) or provide per-sector objectives.

## Refresh datasets
```powershell
.\scripts\refresh_data.ps1
```

Optional API keys:
- `BLS_API_KEY`
- `CENSUS_API_KEY`
- `FRED_API_KEY`

## ML forecasting (CUDA)
Forecasting uses PyTorch when available and will use CUDA automatically if your GPU is detected.

```powershell
pip install -r requirements-ml.txt
```

To install a CUDA-enabled build, edit `requirements-ml.txt` to use the PyTorch CUDA wheel that matches your driver/toolkit.

Optional environment settings:
- `ACS_YEARS` (comma-separated list, e.g. `2018,2019,2020,2021,2022`)
- `FORECAST_REQUIRE_CUDA=1` to fail if CUDA is unavailable

## Generate a memo (API)
```powershell
curl -X POST http://127.0.0.1:8000/api/memo -H "Content-Type: application/json" -d "{\"inputs\":{\"issue_area\":\"labor_market\",\"geography\":{\"level\":\"state\",\"value\":\"Florida\"},\"time_horizon\":\"near_term\",\"budget_sensitivity\":0.5,\"policy_lens\":\"market\"}}"
```

Memos are stored under `outputs/memos/<timestamp>_<hash>/memo.md`.

## Tests
```powershell
.\.venv\Scripts\Activate.ps1
pytest
```

## Notes
- All numeric or dataset-derived claims include dataset citations.
- Policy lens and objectives change policy ranking; evidence is unchanged.
- Administration values live in `data/admin_values.json` (sector weights, objective weights, lens bias).
