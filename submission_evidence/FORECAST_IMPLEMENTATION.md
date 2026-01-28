# FORECAST_IMPLEMENTATION

This document summarizes the forecasting pipeline as implemented in `app/services/forecast.py`.

## Feature table construction & resampling
- `_load_metric_series` loads each metric?s processed dataset (CSV under `data/processed/<dataset_id>/`).
- `_to_monthly_series` parses dates, coerces numeric values, sorts, and resamples to monthly start with forward-fill.
- `_build_feature_table` merges all metric series on date, forward-fills, and drops rows with missing values. Only columns with ?3 non-null values are retained.

**Code excerpt (resampling + fill):**
```python
series = series.resample("MS").mean()
series["value"] = series["value"].ffill()
```

## Models, architectures, and training details
### Per-metric model (Torch MLP)
- Used in `_forecast_with_torch` when torch is available.
- Input window (`lookback`): `min(6, max(2, len(values)-1))`.
- Architecture: Linear(lookback ? 16) ? ReLU ? Linear(16 ? 1).
- Optimizer: Adam, lr=0.01. Loss: MSE.
- Training loop: 200 epochs. Seed: `torch.manual_seed(42)`.

**Code excerpt (training loop length):**
```python
for _ in range(200):
```

### Multifactor model (Torch MLP)
- Used when feature table has ?4 rows and ?3 features.
- Standardization: `(values - mean) / std` (std clamped to ?1e-6).
- Architecture: Linear(n_features ? 32) ? ReLU ? Linear(32 ? n_features).
- Optimizer: Adam, lr=0.01. Loss: MSE.
- Training loop: 250 epochs. Seed: `torch.manual_seed(42)`.

**Code excerpt (training loop length):**
```python
for _ in range(250):
```

## Fallback model & trigger conditions
- `_forecast_series` calls Torch only if `torch` is importable.
- If `FORECAST_REQUIRE_CUDA=1` is set, the code **raises** if CUDA is unavailable.
- If Torch is missing or raises (and CUDA is not required), it falls back to a linear model.
- Linear fallback (`_forecast_with_linear`) uses `np.polyfit` (degree 1) to extrapolate.

**Code excerpt (fallback path):**
```python
return _forecast_with_linear(values, steps)
```

## Forecasted metrics (IDs)
Defined in `METRICS` in `app/services/forecast.py`:
- `labor_unemployment_bls`
- `labor_unemployment_fred`
- `fiscal_real_gdp`
- `housing_median_rent`
- `housing_rent_burden`
- `housing_vacancy_rate`
- `housing_home_value`
- `general_population`
- `education_grad_rate`
- `health_chronic_rate`
- `climate_risk_index`
- `infrastructure_road_condition`
- `environment_pm25`
- `public_safety_violent_crime`
- `energy_retail_price`
- `broadband_access`
- `demographics_net_migration`
- `business_startup_rate`
- `agriculture_yield`

Each metric entry also defines `sector`, `dataset_id`, `value_col`, `date_col`, `unit`, and `preference` in the same file.
