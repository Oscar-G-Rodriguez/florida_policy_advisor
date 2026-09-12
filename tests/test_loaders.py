from pathlib import Path

import requests

from app.data.loaders import bls, census_acs, fred


def test_bls_processor_ignores_non_monthly_periods():
    frame = bls._process_bls_json({"Results": {"series": [{"seriesID": "x", "data": [
        {"year": "2024", "period": "M01", "value": "3.1"},
        {"year": "2024", "period": "M13", "value": "9.9"},
    ]}]}})
    assert frame.to_dict("records") == [{"series_id": "x", "date": "2024-01", "value": 3.1}]


def test_acs_processor_calculates_traceable_ratios():
    payload = [["NAME", "B19013_001E", "B25064_001E", "B17001_002E", "B17001_001E", "B01001_001E", "B25001_001E", "B25002_003E", "B25077_001E", "state", "county"], ["Example County, Florida", "60000", "1500", "100", "1000", "1000", "500", "25", "250000", "12", "001"]]
    frame = census_acs._process_acs_json(payload)
    row = frame.iloc[0]
    assert row["county_fips"] == "12001"
    assert row["poverty_rate"] == 0.1
    assert row["vacancy_rate"] == 0.05
    assert row["rent_to_income"] == 0.3


def test_fred_fetch_uses_series_specific_response(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"observations": [{"date": "2024-01-01", "value": "1.2"}]}

    monkeypatch.setattr(fred.requests, "get", lambda *args, **kwargs: Response())
    assert fred._fetch_series("FLUR", "key") == [{"date": "2024-01-01", "value": "1.2"}]


def test_bls_refresh_failure_is_explicitly_labeled_fixture(monkeypatch, tmp_path):
    fixture = Path(__file__).parents[1] / "data" / "fixtures" / "bls_unemployment" / "unemployment.csv"
    processed = tmp_path / "processed" / "unemployment.csv"
    raw = tmp_path / "raw" / "bls.json"
    monkeypatch.setattr(bls, "processed_path", lambda *_: processed)
    monkeypatch.setattr(bls, "raw_path", lambda *_: raw)
    monkeypatch.setattr(bls, "fixture_path", lambda *_: fixture)
    monkeypatch.setattr(bls, "write_table", lambda *_: None)
    monkeypatch.setattr(bls, "update_dataset_refresh", lambda *args, **kwargs: None)
    monkeypatch.setattr(bls.requests, "post", lambda *args, **kwargs: (_ for _ in ()).throw(requests.RequestException("offline")))
    result = bls.refresh(allow_network=True)
    assert result["status"] == "fixture"
    assert "offline" in result["error"]
    assert processed.exists()
