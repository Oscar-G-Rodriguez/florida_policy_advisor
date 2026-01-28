# RUNBOOK

## Local dev run (backend + frontend)
1) Create & activate venv:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2) Install backend deps:
   ```powershell
   pip install -r requirements.txt
   ```
3) Install frontend deps:
   ```powershell
   cd frontend
   npm install
   cd ..
   ```
4) Start both servers:
   ```powershell
   .\scripts\dev.ps1
   ```
   - Backend: `http://127.0.0.1:8000`
   - Frontend (Vite): `http://127.0.0.1:5173`

## Local dev (frontend-only demo)
```powershell
cd frontend
npm install
npm run dev
```
- If `VITE_API_BASE` is unset and `VITE_REQUIRE_API` is not `true`, the UI runs in **demo mode** (no backend required).

## Packaged EXE build/run
1) Build the single-file executable:
   ```powershell
   .\scripts\build_single_app.ps1
   ```
   Output: `dist\FloridaPolicyAdvisor.exe`
2) Run the EXE:
   - Double-click `dist\FloridaPolicyAdvisor.exe` (opens embedded desktop window).

## Installer build/run
1) Build installer:
   ```powershell
   .\scripts\build_installer.ps1
   ```
2) Run installer:
   - `dist\FloridaPolicyAdvisor-Setup.exe`
   - Or `BuildApp.cmd` (wrapper for the installer script)

## Environment variables
**Backend data refresh (optional):**
- `BLS_API_KEY`, `CENSUS_API_KEY`, `FRED_API_KEY` (used by loaders in `app/data/loaders/*`).
- `ACS_YEARS` (comma-separated list of years for ACS pull).
- `FORCE_OFFLINE=1` (forces loaders to use cached fixtures).

**Forecasting:**
- `FORECAST_REQUIRE_CUDA=1` (fails if CUDA is not available).

**Frontend/API:**
- `VITE_API_BASE` (base URL for the API, default empty string).
- `VITE_REQUIRE_API=true` (forces live API mode; otherwise demo mode is allowed).

**Packaged app host/port:**
- `APP_HOST` (default `127.0.0.1`)
- `APP_PORT` (default `8000`)

## What happens if env vars are missing
- Data loaders fall back to cached fixtures where available (`data/fixtures/*`) and mark refresh as cached.
- If `VITE_API_BASE` is empty and `VITE_REQUIRE_API` is not `true`, the UI uses demo mode.
- If `FORECAST_REQUIRE_CUDA=1` and CUDA is unavailable, forecast generation raises an error instead of falling back.

## Frontend <-> Backend integration
- The React app posts to `${VITE_API_BASE}/api/advice` and `/api/memo` and hits `${VITE_API_BASE}/health`.
- In packaged mode, the API is hosted by the same process via Uvicorn (`app/packaged.py`) and serves the bundled static assets in `app/static`.
