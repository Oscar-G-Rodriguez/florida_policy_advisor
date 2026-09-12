from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _payload(issue_area: str, geography: dict | None = None) -> dict:
    return {
        "issue_area": issue_area,
        "geography": geography or {"level": "state", "value": "Florida"},
        "time_horizon": "near_term",
        "budget_sensitivity": 0.5,
        "policy_lens": "market",
    }


def test_supported_sector_api_paths_are_traceable():
    for issue_area, geography in [
        ("labor_market", None),
        ("housing", {"level": "county", "value": "Miami-Dade County"}),
        ("fiscal", None),
    ]:
        response = client.post("/api/advice", json=_payload(issue_area, geography))
        assert response.status_code == 200
        body = response.json()
        assert body["data_mode"] == "fixture"
        assert "OFFLINE FIXTURE DATA" in body["data_notice"]
        assert body["citations"]
        assert all(citation["data_mode"] == "fixture" for citation in body["citations"])
        if issue_area == "housing":
            assert any("Miami-Dade County, Florida" in item["claim"] for item in body["evidence"])


def test_unsupported_sector_is_rejected_at_the_api_boundary():
    response = client.post("/api/advice", json=_payload("education"))
    assert response.status_code == 422


def test_dataset_endpoint_marks_unimplemented_sources_unavailable():
    response = client.get("/api/datasets")
    assert response.status_code == 200
    datasets = {item["dataset_id"]: item for item in response.json()["datasets"]}
    assert datasets["bls_unemployment"]["availability"] == "supported"
    assert datasets["nces_ccd_grad"]["availability"] == "unavailable"


def test_packaged_static_ui_is_served_by_the_backend():
    response = client.get("/")
    assert response.status_code == 200
    assert "Florida Policy Advisor" in response.text
    assert "/assets/index-" in response.text
