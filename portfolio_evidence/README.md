# Portfolio evidence

This folder contains reproducible artifacts for reviewing the current application, not a competition submission.

- `sample_advice_request.json`: request sent through the FastAPI application path.
- `sample_advice_response.json`: response generated from the checked-in offline fixture. It is intentionally labeled `fixture` and withholds forecasts because the historical series is too short.
- `openapi.json`: API schema exported from the current FastAPI application.
- `data_quality_report.json`: reproducible quality checks for the checked-in processed data.
- `forecast_validation_report.json`: forecast coverage, withholding reasons, and backtest metrics.

For architecture, validation rules, exact test commands, and a browser demo checklist, see `docs/ARCHITECTURE.md` and `docs/VALIDATION.md`.
