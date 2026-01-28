# VALIDATION_RESULTS

## Test commands
- From README (dev):
  - `pytest`
- Backend test runner uses FastAPI TestClient and citation validator tests.

## What tests cover
- `tests/test_api.py`: health endpoint and `/api/advice` response shape.
- `tests/test_citations.py`: citation validator rejects numeric claims without citations.

## Recent test logs
Saved test log: `submission_evidence/pytest_log.txt` (captured from a local pytest run).

## RUN THIS
```powershell
# Activate venv if needed
.\.venv\Scripts\Activate.ps1
pytest
```

## Evaluation / sanity-check scripts
NOT FOUND IN REPO. (If you want a dedicated smoke-test script, add one under `scripts/` and record its output here.)
