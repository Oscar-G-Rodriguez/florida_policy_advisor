# SCORING_EXACT

This file documents the exact scoring math as implemented in the repo. All equations and constants below are traced to code files and data assets.

## Forecast ?pressure? (from `app/services/policy_engine.py:_pressure_scores`)
**Core math** (code excerpt; total quoted words kept minimal):
```python
pressures[item.metric_id] = (severity + baseline_pressure) * objective_weight * sector_weight
```
- `severity = harm / (abs(baseline) + 1e-6)`.
- `harm` depends on metric preference:
  - `lower_is_better`: `harm = max(0, predicted - baseline)`.
  - `higher_is_better`: `harm = max(0, -(predicted - baseline))`.
  - otherwise: `harm = max(0, abs(predicted - baseline))`.
- `baseline_pressure` is from `OBJECTIVE_BASELINE_PRESSURE` (improve: 0.08, stabilize: 0.0, resilience: 0.05).
- `objective_weight` and `sector_weight` are loaded from `data/admin_values.json` via `app/core/values.py`.

## Policy scoring (from `app/services/policy_engine.py:_score_policy`)
**Core math** (code excerpt):
```python
return impact + speed_bonus + equity_bonus + market_bonus - cost_penalty - feasibility_penalty - risk_penalty
```
- `impact` is the sum of `(pressure for metric) * (policy effect)` across the policy?s effects.
- `cost_penalty = normalize_tag(cost) * budget_sensitivity * lens.cost_weight`.
- `speed_bonus = normalize_tag(speed) * lens.speed_weight * (0.2 + urgency)`.
- `equity_bonus = normalize_tag(equity) * lens.equity_weight * lens_bias['equity']`.
- `market_bonus = normalize_tag(market) * lens.market_weight * lens_bias['market']`.
- `feasibility_penalty = normalize_tag(feasibility) * feasibility_weight`.
- `risk_penalty = normalize_tag(risk) * risk_weight`.

**Constants used**
- Lens weights from `app/core/policy_lens.py`:
  - `market`: cost 0.6, speed 0.7, equity 0.2, market 0.8.
  - `equity`: cost 0.4, speed 0.5, equity 0.9, market 0.3.
- Admin values from `data/admin_values.json`:
  - `objective_weights`: improve 1.2, stabilize 1.0, resilience 1.1.
  - `lens_bias`: equity 0.55, market 0.45 (speed/cost also present but unused in `_score_policy`).
  - `feasibility_weight`: 0.35, `risk_weight`: 0.25.
  - `sector_weights`: per-sector multipliers (e.g., housing 1.2, labor_market 1.1, general 0.7).
- Tag normalization from `app/core/policy_lens.py`: low=1.0, medium=2.0, high=3.0.

## Bundle scoring / optimization (from `app/services/policy_engine.py:rank_policies`)
**Combination search** (code excerpt):
```python
for size in range(2, 4):
```
- Bundles are built from **all 2- and 3-policy combinations** among the top 10 scored policies.
- Each bundle is **aggregated** (`_aggregate_bundle`) by summing and clipping effects to [-1, 1] and averaging tag values (cost/speed/equity/market/feasibility/risk).
- Bundle score uses the **same `_score_policy` formula** applied to the aggregate bundle representation.
- Bundles are sorted by score and the **top 3** are returned.

## Objectives, lens, admin values, budget, feasibility, risk
- **Objectives**: determine `baseline_pressure` and select `objective_weight` for each sector in `_pressure_scores`.
- **Policy lens**: selects the lens weights (cost/speed/equity/market) in `_score_policy`.
- **Admin values**: `sector_weights`, `objective_weights`, `lens_bias`, `feasibility_weight`, `risk_weight` all multiply or penalize the score.
- **Budget sensitivity**: multiplies `cost_penalty` directly.
- **Feasibility/Risk**: subtract penalties via normalized tag values.

## Worked example (using repo constants)
Assume a **housing** metric with:
- `baseline = 100`, `predicted = 110`, `preference = lower_is_better`.
- Objective = `improve` (baseline pressure 0.08, weight 1.2).
- Sector weight for housing = 1.2 (from `data/admin_values.json`).

Pressure:
- `delta = 10`, `harm = 10`, `severity = 10 / 100 = 0.10`.
- `pressure = (0.10 + 0.08) * 1.2 * 1.2 = 0.2592`.

Policy scoring for a market lens policy with:
- cost=medium (2), speed=high (3), equity=medium (2), market=high (3), feasibility=medium (2), risk=medium (2)
- budget_sensitivity = 0.5, urgency = 0.3
- effect on the metric = 0.35

Score pieces:
- `impact = 0.2592 * 0.35 = 0.09072`
- `cost_penalty = 2 * 0.5 * 0.6 = 0.6`
- `speed_bonus = 3 * 0.7 * (0.2 + 0.3) = 1.05`
- `equity_bonus = 2 * 0.2 * 0.55 = 0.22`
- `market_bonus = 3 * 0.8 * 0.45 = 1.08`
- `feasibility_penalty = 2 * 0.35 = 0.7`
- `risk_penalty = 2 * 0.25 = 0.5`

Final score:
- `0.09072 + 1.05 + 0.22 + 1.08 - 0.6 - 0.7 - 0.5 = 0.64072`

All formulas and constants above match the code paths listed in this document.
