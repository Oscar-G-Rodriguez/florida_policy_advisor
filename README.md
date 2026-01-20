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

## Refresh datasets
```powershell
.\scripts\refresh_data.ps1
```

Optional API keys:
- `BLS_API_KEY`
- `CENSUS_API_KEY`
- `FRED_API_KEY`

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
- Policy lens changes ranking only; evidence is unchanged.
