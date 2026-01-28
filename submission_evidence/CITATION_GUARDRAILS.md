# CITATION_GUARDRAILS

## Numeric-claim enforcement
`app/core/citations.py` enforces that any numeric claim must include citations. If a numeric string is detected and no citations are provided, it raises a `ValueError`.

**Code excerpt (validator rule):**
```python
if _find_numeric(text) and not list(citations):
```

## Enforcement path + failure handling
- `app/main.py` calls `validate_response_citations` inside `/api/advice` and `/api/memo` handlers.
- Failures raise `ValueError`, which are converted to `HTTPException(status_code=500, detail=...)` in `app/main.py`.

## What gets checked
`validate_response_citations` enforces:
- Response must include a non-empty `citations` list.
- `citation_id` values must be unique.
- Evidence claims with numbers must include citations; the citation IDs must exist in the response citation list.
- Forecast items with `predicted_value` must include citations; citation IDs must exist.
- Summary, options, option pros/cons, implementation notes, and risks **must not contain numeric claims** (those checks pass an empty citation list and therefore error on numeric text).

## Citation schema (from `app/models.py`)
Citation objects include:
- `citation_id` (string key used by evidence/outlook items)
- `dataset_id`
- `url`
- `retrieval_date`
- optional `note`

## How citation metadata is populated
- `app/services/advisor.py:_citation_for` pulls dataset metadata via `app/data/registry.py:get_dataset_metadata`.
- Retrieval dates are read from `data/registry_state.json`. When missing, registry returns `"unknown"`.
