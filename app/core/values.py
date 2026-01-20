from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

ROOT_DIR = Path(__file__).resolve().parents[2]
VALUES_PATH = ROOT_DIR / "data" / "admin_values.json"


@dataclass(frozen=True)
class AdminValues:
    sector_weights: Dict[str, float]
    objective_weights: Dict[str, float]
    lens_bias: Dict[str, float]
    feasibility_weight: float
    risk_weight: float


def _default_values() -> AdminValues:
    return AdminValues(
        sector_weights={},
        objective_weights={"improve": 1.2, "stabilize": 1.0, "resilience": 1.1},
        lens_bias={"equity": 0.5, "market": 0.5, "speed": 0.5, "cost": 0.5},
        feasibility_weight=0.35,
        risk_weight=0.25,
    )


def load_admin_values() -> AdminValues:
    if not VALUES_PATH.exists():
        defaults = _default_values()
        VALUES_PATH.parent.mkdir(parents=True, exist_ok=True)
        VALUES_PATH.write_text(json.dumps(defaults.__dict__, indent=2))
        return defaults
    payload = json.loads(VALUES_PATH.read_text())
    defaults = _default_values()
    return AdminValues(
        sector_weights=payload.get("sector_weights", defaults.sector_weights),
        objective_weights=payload.get("objective_weights", defaults.objective_weights),
        lens_bias=payload.get("lens_bias", defaults.lens_bias),
        feasibility_weight=float(payload.get("feasibility_weight", defaults.feasibility_weight)),
        risk_weight=float(payload.get("risk_weight", defaults.risk_weight)),
    )
