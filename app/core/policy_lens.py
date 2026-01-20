from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class LensWeights:
    cost_weight: float
    speed_weight: float
    equity_weight: float
    market_weight: float


LENSES: Dict[str, LensWeights] = {
    "market": LensWeights(cost_weight=0.6, speed_weight=0.7, equity_weight=0.2, market_weight=0.8),
    "equity": LensWeights(cost_weight=0.4, speed_weight=0.5, equity_weight=0.9, market_weight=0.3),
}


def normalize_tag(value: str | float | int) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    mapping = {"low": 1.0, "medium": 2.0, "high": 3.0}
    return mapping.get(value, 2.0)


def score_option(
    option: Dict[str, str],
    lens: LensWeights,
    budget_sensitivity: float,
    urgency: float = 0.0,
) -> float:
    cost_score = normalize_tag(option.get("cost", "medium"))
    speed_score = normalize_tag(option.get("speed", "medium"))
    equity_score = normalize_tag(option.get("equity", "medium"))
    market_score = normalize_tag(option.get("market", "medium"))

    cost_penalty = cost_score * budget_sensitivity * lens.cost_weight
    urgency = max(0.0, min(1.0, urgency))
    speed_boost = speed_score * lens.speed_weight * urgency
    score = (
        speed_score * lens.speed_weight
        + equity_score * lens.equity_weight
        + market_score * lens.market_weight
        + speed_boost
        - cost_penalty
    )
    return score


def rank_options(
    options: List[Dict[str, str]],
    policy_lens: str,
    budget_sensitivity: float,
    urgency: float = 0.0,
) -> List[Dict[str, str]]:
    lens = LENSES.get(policy_lens, LENSES["market"])
    scored = [
        (score_option(option, lens, budget_sensitivity, urgency), option)
        for option in options
    ]
    scored.sort(key=lambda item: item[0], reverse=True)
    return [option for _, option in scored]
