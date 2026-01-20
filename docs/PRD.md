# Florida Policy Advisor - Product Requirements Document (PRD)

## Problem statement
Florida policymakers need fast, evidence-backed policy advice without requiring technical staff to run complex analyses. The MVP should provide structured options and tradeoffs based on public datasets, with a selectable policy lens that changes prioritization but never the facts.

## Users
- State agency analysts and program managers
- County and municipal policy staff
- Legislative policy aides seeking neutral, evidence-backed options

## Scope
In scope:
- Local-first web app with a simple UI for non-technical users
- Evidence-backed advice for common policy issue areas
- Selectable policy lens that re-ranks options without altering evidence
- Exportable policy memo with citations
- Deterministic, auditable logic
- Dataset refresh with caching for offline use

Out of scope:
- Political persuasion or campaign language
- Personal data or individual-level recommendations
- Real-time or streaming data pipelines
- Optimization of statewide budgets or allocations

## MVP definition
- Backend API with: health, advice generation, dataset listing, dataset refresh
- Frontend SPA with a single workflow to generate advice and export a memo
- Three working dataset loaders (BLS, Census ACS, FRED)
- Evidence section with citations for all numeric or dataset-derived claims
- 3-5 policy options per request, ranked by the selected policy lens

## Data sources plan
- BLS Public API (labor market / unemployment series)
- Census ACS 5-year API (Florida county-level income, rent, poverty)
- FRED API (macro series relevant to Florida policy)

Each dataset has:
- A registry entry with dataset_id, name, description, url, license/terms if known, retrieval_date, refresh_method
- Raw data cached under `data/raw/<dataset_id>/`
- Processed data under `data/processed/<dataset_id>/`
- Optional SQLite tables for quick querying

## Safety and neutrality policy
- No political persuasion or advocacy
- Present options with tradeoffs, constraints, and implementation considerations
- Policy lens affects ranking only, not facts or evidence
- Avoid inference of political affiliation
- Cite every numeric claim or dataset-derived assertion with dataset metadata

## Evaluation plan
What "good" looks like:
- Advice is consistent, deterministic, and auditable
- Evidence section is grounded in datasets with proper citations
- Users can run locally using simple commands from README
- Tests validate API shape and citation enforcement
- Users can export a memo with embedded citations
