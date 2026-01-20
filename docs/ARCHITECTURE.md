# Florida Policy Advisor - Architecture

## Modules
- `app/main.py`: FastAPI app and routes
- `app/core/citations.py`: citation models and validation
- `app/core/policy_lens.py`: lens definitions and ranking logic
- `app/services/advisor.py`: advice pipeline (evidence -> options -> ranking)
- `app/data/registry.py`: dataset registry and refresh tracking
- `app/data/loaders/*`: dataset loaders (BLS, ACS, FRED)
- `app/services/memo.py`: memo generation and export

## API routes
- `GET /health`: basic health check
- `POST /api/advice`: generate advice
  - input: issue_area, geography, time_horizon, budget_sensitivity, policy_lens
  - output: summary, evidence, options, risks, citations
- `GET /api/datasets`: list datasets with last refresh
- `POST /api/refresh`: refresh datasets (idempotent)
- `POST /api/memo`: generate memo markdown and save under `outputs/memos/`

## Data flow
1. User submits `POST /api/advice`.
2. Advisor loads processed data from `data/processed/` (or SQLite if available).
3. Evidence facts are built with numeric values and linked citations.
4. Policy options are assembled from templates and ranked by lens.
5. Response returns evidence, options, risks, and citations.

## Citation flow
- Each dataset has a registry record with `dataset_id`, `url`, and `retrieval_date`.
- Evidence items include `citations` listing citation IDs.
- Response includes a `citations` array of citation objects.
- The citation validator enforces that any numeric claim has citations.

## Frontend data flow
- UI calls `/api/advice` with user selections.
- Results render summary, evidence, and ranked options.
- “Download memo” calls `/api/memo` to persist markdown output and return the file contents for download.

## Storage
- Raw datasets: `data/raw/<dataset_id>/`
- Processed datasets: `data/processed/<dataset_id>/`
- Registry state: `data/registry_state.json`
- Memos: `outputs/memos/<timestamp>_<hash>/memo.md`

## Idempotent refresh
- `POST /api/refresh` re-downloads datasets if possible.
- On failure, it reuses cached data and still updates status.
