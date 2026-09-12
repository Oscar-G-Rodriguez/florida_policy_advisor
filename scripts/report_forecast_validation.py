from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.models import AdviceRequest  # noqa: E402
from app.services.forecast import generate_outlook  # noqa: E402


REQUESTS = [
    ("labor_market", {"level": "state", "value": "Florida"}),
    ("fiscal", {"level": "state", "value": "Florida"}),
    ("housing", {"level": "county", "value": "Miami-Dade County"}),
]


def main() -> None:
    forecasts = []
    for issue_area, geography in REQUESTS:
        request = AdviceRequest(
            issue_area=issue_area,
            geography=geography,
            time_horizon="near_term",
            budget_sensitivity=0.5,
            policy_lens="market",
        )
        outlook, _, _, _ = generate_outlook(request)
        forecasts.extend(item.model_dump() for item in outlook)
    payload = {
        "generated_at": date.today().isoformat(),
        "forecast_count": len(forecasts),
        "available_count": sum(item["status"] == "available" for item in forecasts),
        "withheld_count": sum(item["status"] != "available" for item in forecasts),
        "forecasts": forecasts,
    }
    output = ROOT_DIR / "portfolio_evidence" / "forecast_validation_report.json"
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
