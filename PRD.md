# Florida Workforce Stability Policy Advisor (MVP) — PRD

## 1) Purpose
Create a local-first web application that helps Florida policymakers anticipate near-term workforce strain and compare policy options under configurable prioritization lenses.

Primary outputs:
- County-by-month risk scores (next 1–3 months) for:
  - Agriculture
  - Construction
- Ranked policy options with per-option tradeoffs and lead time.

Non-negotiables:
- The app must not ask for party affiliation.
- The app must not produce persuasive campaign language.
- Recommendations must be expressed as options, tradeoffs, and constraints.

## 2) Primary users and workflows
Users:
- County and municipal staff (planning, procurement, workforce boards)
- State-level program staff (workforce, economic development)

Workflow:
1. Select a Florida county.
2. View next 1–3 months risk (ag + construction) with a brief explanation of key drivers.
3. Choose a policy lens via sliders/weights.
4. Receive a ranked list of interventions with “why”, lead time, and tradeoffs.
5. Export a short brief (HTML download) for internal review.

## 3) MVP scope
In scope:
- Florida only.
- One working ingestion pipeline from a public source, with caching.
- A fast, interpretable ML model that produces a 3-level risk class per county-month.
- A deterministic policy-ranking module based on lens weights.
- A minimal web UI served locally.
- Automated tests.

Out of scope (MVP):
- Individual-level predictions.
- Live integrations with private systems.
- Any enforcement, surveillance, or eligibility screening.
- Full statewide portfolio optimization.

## 4) Data requirements
At least one real ingestion pipeline is required.

Preferred dataset for MVP (manageable and public):
- DOL OFLC H-2A disclosure data (CSV) for legal seasonal agricultural labor signal.

Optional dataset (future):
- BLS QCEW county employment by NAICS for construction and broader labor signals.

Data processing outputs:
- A county-month table containing features for modeling.
- Cached raw download and cached processed table.

Resilience to download issues:
- Include a small repository fixture (sample CSV) as a fallback so the demo and tests remain runnable offline.

## 5) Modeling requirements
We need an ML model that is quick to train and simple to validate.

Proposed label (proxy):
- Define a “strain event” for agriculture as a statistically large negative change in approved positions (or a related count) relative to a trailing window.
- For construction, if the optional dataset is not implemented in MVP, provide a synthetic demo series and keep construction as a stub with explicit TODO.

Model class:
- Logistic regression or gradient boosted trees (sklearn) for binary event prediction.
- Convert probability to Low/Med/High by fixed thresholds.

Explainability:
- Provide top 3 drivers per prediction (feature coefficients or tree feature importances).

## 6) Policy recommendation requirements
Policy library:
- 8–12 interventions stored in code, each with:
  - id, title
  - sector relevance: ag and/or construction
  - lead_time_days (integer)
  - cost_bucket: low | medium | high
  - expected_effect: short text (directional)
  - tradeoffs: short text

Policy lens inputs (UI sliders 0.0–1.0):
- budget_sensitivity
- speed_preference
- worker_protection_weight
- local_employment_weight

Ranking rules (deterministic):
- Combine:
  - sector match to current risk
  - lead time fit vs speed_preference
  - cost fit vs budget_sensitivity
  - worker_protection and local_employment weight boosts
- Return a ranked list with a short “why” statement per intervention.

## 7) User interface requirements
Minimum pages:
1. Home: county selector and a compact summary.
2. County detail: next 1–3 months risk table (ag + construction) and top drivers.
3. Recommendations: sliders + ranked interventions.
4. Export: “Download brief” that generates an HTML report.

Accessibility:
- Keyboard navigation works.
- High contrast default styling.

## 8) Backend and API requirements
Backend:
- Python 3.11+
- FastAPI
- SQLite for processed tables and run metadata

Endpoints:
- GET /api/counties
  - returns: [{"fips": "12086", "name": "Miami-Dade"}, ...]
- GET /api/forecast?county_fips=12086
  - returns a JSON object with:
    - county
    - horizon_months
    - rows: [{"month": "2025-11", "ag_risk": "medium", "con_risk": "low", "drivers": {...}}, ...]
- POST /api/recommendations
  - body: {"county_fips": "12086", "months": ["2025-11","2025-12"], "lens": {...}}
  - returns: ranked list of interventions with “why” and tradeoffs
- GET /export/brief?county_fips=12086
  - returns: downloadable HTML

## 9) Testing and validation requirements
Automated tests:
- Unit tests:
  - policy ranking determinism
  - feature builder output schema
- Integration tests:
  - ingestion (mocked network or uses fixture)
  - train + predict pipeline
  - API endpoints return expected schema

Validation output (MVP):
- Backtest-style evaluation on historical months using the proxy label:
  - report basic metrics: precision, recall, AUROC (when data permits)
- If data volume is insufficient, generate and report a held-out evaluation on the available range and document the limitation.

## 10) Security and ethics
- No personal data.
- No party inference.
- No persuasion content.
- Document limits and uncertainty.

## 11) Local run requirements
- One command to start the app:
  - python -m app.main
- One command to run tests:
  - python -m pytest

## 12) Definition of done (MVP)
Done means:
- App starts locally and renders the UI.
- /api/counties, /api/forecast, /api/recommendations work.
- At least one public dataset ingestion runs successfully OR the fixture fallback is used with a clear banner.
- Model training and prediction runs end-to-end.
- Export brief downloads.
- Tests pass.
