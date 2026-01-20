[
  {
    "id": "setup-001",
    "category": "setup",
    "description": "Initialize repo structure, Python project metadata, and baseline tooling",
    "steps": [
      "Create Python package layout under src/",
      "Create pyproject.toml with dependencies (fastapi, uvicorn, pandas, numpy, scikit-learn, sqlalchemy, pydantic, httpx, pytest)",
      "Create .gitignore for venv, .pytest_cache, data/cache, sqlite db",
      "Add a minimal README with run/test commands",
      "Run: python -m pytest (no tests yet is acceptable if collected ok)"
    ],
    "passes": false
  },
  {
    "id": "backend-001",
    "category": "backend",
    "description": "Create FastAPI app skeleton and health endpoint",
    "steps": [
      "Implement app/main.py with FastAPI instance",
      "Add GET /health returning {status: 'ok'}",
      "Add uvicorn entry in README",
      "Add test for /health using TestClient"
    ],
    "passes": false
  },
  {
    "id": "data-001",
    "category": "data",
    "description": "Implement county reference table for Florida (minimal)",
    "steps": [
      "Create a small CSV/JSON with Florida county FIPS and names (static asset in repo)",
      "Load it on startup and expose GET /api/counties",
      "Add test asserting non-empty list and expected keys"
    ],
    "passes": false
  },
  {
    "id": "data-002",
    "category": "data",
    "description": "Implement one public ingestion pipeline with caching and fixture fallback",
    "steps": [
      "Implement app/data/ingest_h2a.py that downloads a public H-2A disclosure CSV (or documented stable URL) and caches raw file",
      "Add repo fixture in app/data/fixtures/h2a_sample.csv",
      "If download fails, load fixture and set a flag used by UI",
      "Add test that ingestion returns a DataFrame with required columns and sets fallback flag when forced"
    ],
    "passes": false
  },
  {
    "id": "features-001",
    "category": "features",
    "description": "Build county-month feature table and store in SQLite",
    "steps": [
      "Implement app/data/features.py to aggregate the ingested table into county-month rows",
      "Compute a small set of numeric features (counts, rolling deltas, simple seasonality)",
      "Persist features to SQLite via SQLAlchemy",
      "Add test for schema and row count > 0"
    ],
    "passes": false
  },
  {
    "id": "model-001",
    "category": "model",
    "description": "Train a lightweight ML model and generate Low/Med/High risk outputs",
    "steps": [
      "Define a proxy label from historical months (event when a target series drops beyond a threshold)",
      "Train logistic regression or gradient boosting model (sklearn)",
      "Calibrate thresholds for Low/Med/High",
      "Expose GET /api/forecast?county_fips=...",
      "Return top 3 drivers per month",
      "Add tests for response schema"
    ],
    "passes": false
  },
  {
    "id": "policy-001",
    "category": "policy",
    "description": "Implement deterministic policy ranking engine with lens inputs",
    "steps": [
      "Create app/policy/library.py with 8\u201312 interventions and metadata",
      "Create app/policy/rank.py that ranks interventions using lens weights and current risks",
      "Expose POST /api/recommendations",
      "Add tests: deterministic ordering given fixed inputs"
    ],
    "passes": false
  },
  {
    "id": "ui-001",
    "category": "ui",
    "description": "Implement minimal HTML UI served by FastAPI",
    "steps": [
      "Serve HTML pages from app/web/ (Jinja2 templates or simple static)",
      "Home page: county selector",
      "County page: risk table",
      "Recommendations page: lens sliders + ranked list",
      "Show a clear banner if fixture fallback was used",
      "Add a basic UI smoke test (request returns 200)"
    ],
    "passes": false
  },
  {
    "id": "export-001",
    "category": "export",
    "description": "Export a short HTML brief",
    "steps": [
      "Implement GET /export/brief?county_fips=... returning HTML download",
      "Include forecast table and ranked interventions",
      "Add test that endpoint returns text/html"
    ],
    "passes": false
  },
  {
    "id": "qa-001",
    "category": "qa",
    "description": "End-to-end test and local run documentation",
    "steps": [
      "Add integration test: ingestion -> features -> train -> forecast -> recommendations",
      "Confirm python -m pytest passes",
      "Confirm python -m app.main starts app",
      "Update README with a short demo script"
    ],
    "passes": false
  }
]
