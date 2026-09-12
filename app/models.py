from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class Geography(BaseModel):
    level: Literal["state", "county"]
    value: str = Field(..., description="State name or county FIPS/name")


class AdviceRequest(BaseModel):
    issue_area: Literal["all", "labor_market", "housing", "fiscal"]
    geography: Geography
    time_horizon: str
    budget_sensitivity: float = Field(..., ge=0.0, le=1.0)
    policy_lens: str
    objective_mode: Literal["improve", "stabilize", "resilience"] = "improve"
    objectives: Optional[Dict[str, Literal["improve", "stabilize", "resilience"]]] = None


class Citation(BaseModel):
    citation_id: str
    dataset_id: str
    url: str
    retrieval_date: str
    note: Optional[str] = None
    geography: Optional[str] = None
    date_range: Optional[str] = None
    data_mode: Literal["live", "fixture", "unknown"] = "unknown"


class EvidenceItem(BaseModel):
    label: str
    claim: str
    citations: List[str] = Field(default_factory=list)


class PolicyOption(BaseModel):
    title: str
    description: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    implementation_notes: str
    sectors: List[str] = Field(default_factory=list)
    impact: Optional[Dict[str, float]] = None
    scoring_note: str = "Heuristic ranking; it is not an estimate of policy impact or causality."


class ForecastItem(BaseModel):
    metric_id: str
    sector: str
    metric: str
    horizon: str
    predicted_value: Optional[float] = None
    baseline_value: Optional[float] = None
    unit: Optional[str] = None
    direction: str
    citations: List[str] = Field(default_factory=list)
    status: Literal["available", "limited", "unavailable"] = "available"
    method_note: Optional[str] = None
    evaluation_note: Optional[str] = None
    uncertainty: Optional[float] = None
    validation_metrics: Dict[str, float] = Field(default_factory=dict)


class PolicyBundle(BaseModel):
    name: str
    policies: List[PolicyOption] = Field(default_factory=list)
    score: float
    rationale: str
    tradeoffs: List[str] = Field(default_factory=list)
    scoring_note: str = "Heuristic ranking; it is not an estimate of policy impact or causality."


class AdviceResponse(BaseModel):
    summary: str
    outlook_summary: str = ""
    outlook: List[ForecastItem] = Field(default_factory=list)
    forecast_info: str = ""
    objectives: Dict[str, str] = Field(default_factory=dict)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    options: List[PolicyOption] = Field(default_factory=list)
    policy_bundles: List[PolicyBundle] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    data_mode: Literal["live", "fixture", "mixed", "unknown"] = "unknown"
    data_notice: str = ""


class MemoRequest(BaseModel):
    inputs: AdviceRequest
    advice: Optional[AdviceResponse] = None


class MemoResponse(BaseModel):
    memo_path: str
    memo_markdown: str
