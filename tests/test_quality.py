import pandas as pd

from app.data.quality import assess_dataset


def test_quality_report_detects_duplicate_keys_and_invalid_rates():
    frame = pd.DataFrame({
        "series_id": ["FLUR", "FLUR"],
        "date": ["2024-01-01", "2024-01-01"],
        "value": [3.1, -2.0],
    })
    report = assess_dataset("fred_macro", frame)
    assert report["status"] == "fail"
    assert report["duplicate_key_rows"] == 2
    assert report["invalid_value_rows"] == 1


def test_quality_report_captures_series_coverage_and_dates():
    frame = pd.DataFrame({
        "series_id": ["FLUR", "FLUR"],
        "date": ["2024-01-01", "2024-02-01"],
        "value": [3.1, 3.2],
    })
    report = assess_dataset("fred_macro", frame)
    assert report["status"] == "pass"
    assert report["series_counts"] == {"FLUR": 2}
    assert report["date_range"] == {"start": "2024-01-01", "end": "2024-02-01"}
