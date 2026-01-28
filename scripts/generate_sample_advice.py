from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.main import app  # noqa: E402


def main() -> None:
    output_dir = Path("submission_evidence")
    output_dir.mkdir(parents=True, exist_ok=True)

    request_payload = {
        "issue_area": "labor_market",
        "geography": {"level": "state", "value": "Florida"},
        "time_horizon": "near_term",
        "budget_sensitivity": 0.5,
        "policy_lens": "market",
    }

    client = TestClient(app)
    response = client.post("/api/advice", json=request_payload)
    response.raise_for_status()

    (output_dir / "sample_advice_request.json").write_text(
        json.dumps(request_payload, indent=2), encoding="utf-8"
    )
    (output_dir / "sample_advice_response.json").write_text(
        json.dumps(response.json(), indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
