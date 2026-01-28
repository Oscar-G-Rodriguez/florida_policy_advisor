from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Tuple

from app.core.policy_lens import LENSES, normalize_tag
from app.core.values import load_admin_values
from app.models import AdviceRequest, ForecastItem, PolicyOption, PolicyBundle
from app.services.forecast import METRICS
from app.services.policy_library import get_policy_options


@dataclass(frozen=True)
class MetricContext:
    sector: str
    preference: str


METRIC_CONTEXT: Dict[str, MetricContext] = {
    spec.metric_id: MetricContext(sector=spec.sector, preference=spec.preference)
    for spec in METRICS
}

OBJECTIVE_BASELINE_PRESSURE = {
    "improve": 0.08,
    "stabilize": 0.0,
    "resilience": 0.05,
}


def _sector_objectives(request: AdviceRequest) -> Dict[str, str]:
    objectives: Dict[str, str] = {}
    if request.objectives:
        objectives.update(request.objectives)
    if request.issue_area == "all":
        sectors = {spec.sector for spec in METRICS}
    else:
        sectors = {request.issue_area}
    sectors.update(objectives.keys())
    for sector in sectors:
        objectives.setdefault(sector, request.objective_mode)
    return objectives


def _pressure_scores(outlook: List[ForecastItem], objectives: Dict[str, str]) -> Dict[str, float]:
    values = load_admin_values()
    pressures: Dict[str, float] = {}
    for item in outlook:
        if item.baseline_value is None or item.predicted_value is None:
            continue
        context = METRIC_CONTEXT.get(item.metric_id)
        if context is None:
            continue
        sector_weight = values.sector_weights.get(context.sector, 1.0)
        objective = objectives.get(context.sector, "improve")
        objective_weight = values.objective_weights.get(objective, 1.0)
        baseline = item.baseline_value
        delta = item.predicted_value - baseline
        if context.preference == "lower_is_better":
            harm = max(0.0, delta)
        elif context.preference == "higher_is_better":
            harm = max(0.0, -delta)
        else:
            harm = max(0.0, abs(delta))
        severity = harm / (abs(baseline) + 1e-6)
        baseline_pressure = OBJECTIVE_BASELINE_PRESSURE.get(objective, 0.0)
        pressures[item.metric_id] = (severity + baseline_pressure) * objective_weight * sector_weight
    return pressures


def _score_policy(policy: Dict[str, object], pressures: Dict[str, float], request: AdviceRequest, urgency: float) -> float:
    values = load_admin_values()
    lens = LENSES.get(request.policy_lens, LENSES["market"])

    impact = 0.0
    effects = policy.get("effects", {}) or {}
    for metric_id, effect in effects.items():
        pressure = pressures.get(metric_id, 0.0)
        impact += pressure * float(effect)

    cost_penalty = normalize_tag(policy.get("cost", "medium")) * request.budget_sensitivity * lens.cost_weight
    speed_score = normalize_tag(policy.get("speed", "medium"))
    equity_score = normalize_tag(policy.get("equity", "medium"))
    market_score = normalize_tag(policy.get("market", "medium"))

    speed_bonus = speed_score * lens.speed_weight * (0.2 + urgency)
    equity_bonus = equity_score * lens.equity_weight * values.lens_bias.get("equity", 0.5)
    market_bonus = market_score * lens.market_weight * values.lens_bias.get("market", 0.5)

    feasibility_penalty = normalize_tag(policy.get("feasibility", "medium")) * values.feasibility_weight
    risk_penalty = normalize_tag(policy.get("risk", "medium")) * values.risk_weight

    return impact + speed_bonus + equity_bonus + market_bonus - cost_penalty - feasibility_penalty - risk_penalty


def _policy_to_response(policy: Dict[str, object]) -> PolicyOption:
    return PolicyOption(
        title=str(policy.get("title")),
        description=str(policy.get("description")),
        pros=[str(policy.get("pros"))],
        cons=[str(policy.get("cons"))],
        implementation_notes=str(policy.get("implementation_notes")),
        sectors=list(policy.get("sectors", [])),
        impact=policy.get("effects", {}),
    )


def _aggregate_bundle(bundle: List[Dict[str, object]]) -> Dict[str, object]:
    effects: Dict[str, float] = {}
    for policy in bundle:
        for metric_id, effect in (policy.get("effects", {}) or {}).items():
            effects[metric_id] = max(-1.0, min(1.0, effects.get(metric_id, 0.0) + float(effect)))

    def _avg_tag(tag: str) -> float:
        scores = [normalize_tag(p.get(tag, "medium")) for p in bundle]
        return sum(scores) / len(scores)

    return {
        "effects": effects,
        "cost": _avg_tag("cost"),
        "speed": _avg_tag("speed"),
        "equity": _avg_tag("equity"),
        "market": _avg_tag("market"),
        "feasibility": _avg_tag("feasibility"),
        "risk": _avg_tag("risk"),
        "sectors": sorted({sector for policy in bundle for sector in policy.get("sectors", [])}),
    }


def _bundle_rationale(bundle: List[Dict[str, object]], pressures: Dict[str, float]) -> Tuple[str, List[str]]:
    combined_effects: Dict[str, float] = {}
    for policy in bundle:
        for metric_id, effect in (policy.get("effects", {}) or {}).items():
            combined_effects[metric_id] = combined_effects.get(metric_id, 0.0) + float(effect)

    ranked_metrics = sorted(
        combined_effects.items(),
        key=lambda item: pressures.get(item[0], 0.0) * item[1],
        reverse=True,
    )
    top_metrics = [metric for metric, _ in ranked_metrics[:3]]
    rationale = "Targets " + ", ".join(top_metrics) if top_metrics else "Broad multi-sector coverage"

    tradeoffs = [
        metric for metric, effect in combined_effects.items()
        if effect < 0 and pressures.get(metric, 0.0) > 0
    ]
    return rationale, tradeoffs


def rank_policies(request: AdviceRequest, outlook: List[ForecastItem], urgency: float) -> Tuple[List[PolicyOption], List[PolicyBundle], Dict[str, str]]:
    objectives = _sector_objectives(request)
    pressures = _pressure_scores(outlook, objectives)

    policies = get_policy_options(request.issue_area)
    scored = []
    for policy in policies:
        score = _score_policy(policy, pressures, request, urgency)
        scored.append((score, policy))
    scored.sort(key=lambda item: item[0], reverse=True)

    top_options = [_policy_to_response(policy) for _, policy in scored[:8]]

    bundles: List[PolicyBundle] = []
    for size in range(2, 4):
        for combo in combinations([policy for _, policy in scored[:10]], size):
            aggregate = _aggregate_bundle(list(combo))
            bundle_score = _score_policy(aggregate, pressures, request, urgency)
            rationale, tradeoffs = _bundle_rationale(list(combo), pressures)
            bundles.append(PolicyBundle(
                name=" + ".join([policy["title"] for policy in combo]),
                policies=[_policy_to_response(policy) for policy in combo],
                score=round(bundle_score, 3),
                rationale=rationale,
                tradeoffs=tradeoffs,
            ))

    bundles.sort(key=lambda item: item.score, reverse=True)
    return top_options, bundles[:3], objectives
