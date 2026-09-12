import numpy as np
import pytest
import pandas as pd

from app.models import AdviceRequest, Geography
from app.services.forecast import _forecast, _select_acs_geography, _temporal_evaluation, generate_outlook


def test_minimum_data_withholds_forecast():
    predictions, status, note, uncertainty, metrics = _forecast(np.array([1.0, 2.0, 3.0]), 1, 1)
    assert predictions is None
    assert status == "unavailable"
    assert "Needs at least 12" in note
    assert uncertainty is None
    assert metrics == {}


def test_horizon_limit_withholds_annual_forecast():
    values = np.arange(6, dtype=float)
    predictions, status, note, _, metrics = _forecast(values, 4, 12)
    assert predictions is None
    assert status == "limited"
    assert "conservative 3-step limit" in note
    assert metrics == {}


def test_temporal_evaluation_prefers_naive_for_flat_series():
    method, metrics = _temporal_evaluation(np.ones(12))
    assert method == "naive"
    assert metrics["naive_mae"] == 0
    assert metrics["linear_mae"] == pytest.approx(0)
    assert metrics["holdout_points"] >= 2


def test_forecast_records_comparable_backtest_metrics():
    predictions, status, _, uncertainty, metrics = _forecast(np.arange(12, dtype=float), 1, 1)
    assert status == "available"
    assert predictions is not None
    assert uncertainty == metrics["selected_mae"]
    assert {"naive_mae", "linear_mae", "naive_rmse", "linear_rmse", "selected_rmse"}.issubset(metrics)


def test_state_housing_requires_complete_county_coverage():
    frame = pd.DataFrame({
        "year": [2022, 2022],
        "county_fips": ["12086", "12095"],
        "county_name": ["Miami-Dade", "Orange"],
        "population": [10, 20],
        "median_gross_rent": [1000, 2000],
        "rent_to_income": [0.2, 0.3],
        "vacancy_rate": [0.1, 0.2],
        "median_home_value": [100000, 200000],
    })
    assert _select_acs_geography(frame, Geography(level="state", value="Florida")).empty


def test_packaged_fixture_outlook_is_withheld_not_predicted():
    request = AdviceRequest(
        issue_area="labor_market",
        geography={"level": "state", "value": "Florida"},
        time_horizon="near_term",
        budget_sensitivity=0.5,
        policy_lens="market",
    )
    outlook, _, _, _ = generate_outlook(request)
    assert outlook
    assert all(item.status != "available" for item in outlook)
    assert all(item.predicted_value is None for item in outlook)
