# Florida Policy Advisor

A local-first policy analysis app that generates evidence-backed advice, multi-sector forecasts, and prioritized policy bundles. Designed for Windows and non-technical users.

---

## Quick start (dev)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd frontend
npm install
cd ..
.\scripts\dev.ps1
```
- Backend: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:5173

---

## Full initialization guide (step-by-step)

### 1) Prerequisites
- Python 3.11+ (3.12 recommended)
- Node.js 18+

### 2) Create a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Install backend dependencies
```powershell
pip install -r requirements.txt
```

### 4) Install frontend dependencies
```powershell
cd frontend
npm install
cd ..
```

### 5) Run the app (dev)
```powershell
.\scripts\dev.ps1
```

### 6) (Optional) Add API keys
Create a `.env` file in the repo root:
```text
BLS_API_KEY=your_key
CENSUS_API_KEY=your_key
FRED_API_KEY=your_key
```
These keys are optional but recommended to refresh live datasets.

### 7) Refresh datasets
```powershell
.\scripts\refresh_data.ps1
```

---

## Single-install app (Windows)

### Build a single EXE
```powershell
.\scripts\build_single_app.ps1
```
Output:
- `dist\FloridaPolicyAdvisor.exe`

### Build a Windows installer (two clicks)
- Double-click `BuildApp.cmd`
- Then run `dist\FloridaPolicyAdvisor-Setup.exe`

The installer creates a Start Menu entry and a desktop shortcut.

---

## Frontend-only (no backend)
```powershell
cd frontend
npm install
npm run dev
```
This runs in demo mode by default. To point at a deployed API:
```powershell
$env:VITE_API_BASE="https://your-api.example.com"
$env:VITE_REQUIRE_API="true"
npm run dev
```

---

## How the app works (detailed)

### 1) Data ingestion
The backend loads datasets from `data/processed/<dataset_id>/`:
- If processed files exist, they are used directly.
- If not, loaders pull from public APIs and cache raw + processed files.

Key datasets (current):
- BLS LAUS (unemployment)
- FRED (GDP, unemployment)
- Census ACS (income, rent, poverty, home value, vacancy, rent burden)

Additional sector datasets are registered in `app/data/registry.py`. These can be loaded via:
- Direct HTTP API loaders (future expansion)
- Drop-in CSVs in `data/processed/<dataset_id>/metrics.csv`
- Drop-in CSVs in `data/processed/<dataset_id>/<metric_id>.csv`

### 2) Feature table + multi-factor forecast
The forecasting pipeline builds a monthly-aligned feature table:
- Each metric is resampled to monthly frequency.
- All metrics are merged by date and forward-filled.
- A multifactor neural model predicts the next step for all metrics at once.

Forecast logic:
- If CUDA is available and PyTorch is installed, a small MLP trains on GPU.
- If CUDA is unavailable, the model falls back to CPU.
- If multifactor prediction is not possible (too few features), a per-metric model is used instead.

Key files:
- `app/services/forecast.py`

### 3) Objectives and administration values
Each sector can have its own objective:
- improve
- stabilize
- resilience

These objectives affect how forecast “pressure” is computed.
Administration weights are stored in:
- `data/admin_values.json`

You can adjust:
- sector_weights
- objective_weights
- lens_bias
- feasibility_weight
- risk_weight

### 4) Policy library and effects matrix
Policies are stored in `app/services/policy_library.py` with:
- cost, speed, equity, market, feasibility, risk
- affected sectors
- effects on metrics (positive or negative strength)

### 5) Policy scoring and bundles
The policy engine:
- Converts forecast deltas into pressure scores
- Applies objective weights and sector weights
- Scores each policy using effects + lens + budget + feasibility
- Builds multi-policy bundles (2–3 policies) and ranks them

Key file:
- `app/services/policy_engine.py`

### 6) Evidence + citations
Every numeric claim must have a dataset citation.
- Evidence is generated from datasets and included in the response.
- Citations are validated server-side.

Key files:
- `app/core/citations.py`
- `app/services/advisor.py`

### 7) Outputs
- Advice and memos are returned via API
- Memos are saved to `outputs/memos/<timestamp>_<hash>/memo.md`

---

## API reference (core endpoints)
- `GET /health` — server status
- `GET /api/datasets` — list datasets + refresh metadata
- `POST /api/refresh` — refresh datasets
- `POST /api/advice` — generate advice (multi-sector)
- `POST /api/memo` — generate and save memo

Example:
```powershell
curl -X POST http://127.0.0.1:8000/api/advice -H "Content-Type: application/json" -d "{\"issue_area\":\"all\",\"geography\":{\"level\":\"state\",\"value\":\"Florida\"},\"time_horizon\":\"near_term\",\"budget_sensitivity\":0.5,\"policy_lens\":\"market\",\"objective_mode\":\"improve\",\"objectives\":{\"housing\":\"improve\",\"fiscal\":\"stabilize\"}}"
```

---

## Environment variables
Common:
- `BLS_API_KEY`
- `CENSUS_API_KEY`
- `FRED_API_KEY`
- `ACS_YEARS` (comma-separated years to pull)

Forecasting:
- `FORECAST_REQUIRE_CUDA=1` (fail if CUDA not available)

CORS (for deployed frontend):
- `CORS_ORIGINS=http://localhost:5173,https://your-frontend.example.com`

---

## ML forecasting (CUDA)
Install optional ML dependencies:
```powershell
pip install -r requirements-ml.txt
```
To use CUDA, replace the `torch==...` line in `requirements-ml.txt` with your CUDA wheel.

---

## Tests
```powershell
.\.venv\Scripts\Activate.ps1
pytest
```

---

## Troubleshooting
- If datasets are empty, run `.\scripts\refresh_data.ps1`.
- If forecasts are missing, ensure each metric has at least 3 time points.
- If the installer is missing, rebuild with `BuildApp.cmd`.
- If the desktop shortcut is missing, re-run the installer and keep “Create a desktop icon” checked.
