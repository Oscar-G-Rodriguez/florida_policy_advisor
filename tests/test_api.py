from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_advice_shape():
    payload = {
        "issue_area": "labor_market",
        "geography": {"level": "state", "value": "Florida"},
        "time_horizon": "near_term",
        "budget_sensitivity": 0.5,
        "policy_lens": "market",
    }
    response = client.post("/api/advice", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "outlook_summary" in data
    assert "outlook" in data
    assert "forecast_info" in data
    assert "objectives" in data
    assert "evidence" in data
    assert "options" in data
    assert "policy_bundles" in data
    assert "risks" in data
    assert "citations" in data
    assert len(data["citations"]) >= 1
