# Validation report

## Reproducible sample request

```json
{
  "issue_area": "housing",
  "geography": {"level": "county", "value": "Miami-Dade County"},
  "time_horizon": "near_term",
  "budget_sensitivity": 0.7,
  "policy_lens": "equity",
  "objective_mode": "improve"
}
```

Run it against the live backend:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/advice -ContentType 'application/json' -Body (Get-Content .\portfolio_evidence\sample_advice_request.json -Raw)
```

The response must include `data_mode`, `data_notice`, per-item citation IDs, and source metadata. A fixture response must contain `OFFLINE FIXTURE DATA`; it is not a live result.

## Forecast validation rules

| Rule | Behavior |
| --- | --- |
| Monthly data fewer than 12 observations | Forecast withheld |
| Annual/quarterly data fewer than 6 observations | Forecast withheld |
| Monthly horizon over 12 steps | Forecast withheld |
| Annual/quarterly horizon over 3 steps | Forecast withheld |
| Sufficient data | Naive last-value and linear trend are evaluated on chronological holdouts; only the lower-MAE method is used |

The checked-in fixture contains only three observations for BLS/FRED series and three annual ACS observations. It therefore produces no forecast, which is the intended credibility guardrail. Live forecasts are marked as evaluated baselines, not accuracy claims or causal estimates.

## Data-quality metrics

`scripts/validate_data.py` writes `portfolio_evidence/data_quality_report.json`. Per supported dataset, it reports row and column counts, schema fingerprint, required-column null rates, duplicate key rows, invalid-value rows, date range, and per-series row counts. Refresh records preserve the same checks with the source mode and error context. These are quality metrics, not claims of public-policy impact.

A structural `pass` does not mean the source is current. Review `data_mode`, `retrieval_date`, and `source_age_days` alongside the report.

`scripts/report_forecast_validation.py` writes `portfolio_evidence/forecast_validation_report.json`. It records each supported forecast's availability status, withheld reason, selected method, uncertainty, and candidate MAE/RMSE metrics when enough history exists.

## Offline test command

```powershell
pytest -q
```

The suite covers API paths for all three supported sectors, unsupported-sector rejection, citation failures, memo disclaimers, loader processors, temporal validation, forecast withholding, and state-coverage protection for ACS aggregation.

## Frontend browser smoke test

1. Start the backend and frontend with `scripts/dev.ps1`.
2. Verify the input selector offers only Labor market, Housing, Fiscal outlook, and Supported sectors.
3. Generate a Miami-Dade housing request. Confirm a prominent `FIXTURE` source notice appears before evidence and that output says it is not current analysis.
4. Confirm outlook cards report unavailable/limited rather than numeric forecasts for the bundled fixture.
5. Download a memo and verify it includes the data-mode notice, heuristic-score disclaimer, and citations.
6. Refresh with live credentials, regenerate the request, and confirm the source notice changes to `LIVE` only after the loader reports a successful download.

## Validation result

The backend test suite passed offline using the bundled Python runtime. The production Vite build also completed successfully using the pinned frontend dependencies; its verified output was copied into `app/static/` for the desktop application.
