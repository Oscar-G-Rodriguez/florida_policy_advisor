from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class Geography(BaseModel):
    level: Literal["state", "county"]
    value: str = Field(..., description="State name or county FIPS/name")


class AdviceRequest(BaseModel):
    issue_area: str
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


class EvidenceItem(BaseModel):
    label: str
    claim: str
    citations: List[str]


class PolicyOption(BaseModel):
    title: str
    description: str
    pros: List[str]
    cons: List[str]
    implementation_notes: str
    sectors: List[str] = []
    impact: Optional[Dict[str, float]] = None


class ForecastItem(BaseModel):
    metric_id: str
    sector: str
    metric: str
    horizon: str
    predicted_value: float
    baseline_value: Optional[float] = None
    unit: Optional[str] = None
    direction: str
    citations: List[str]
    method_note: Optional[str] = None


class PolicyBundle(BaseModel):
    name: str
    policies: List[PolicyOption]
    score: float
    rationale: str
    tradeoffs: List[str]


class AdviceResponse(BaseModel):
    summary: str
    outlook_summary: str = ""
    outlook: List[ForecastItem] = []
    forecast_info: str = ""
    objectives: Dict[str, str] = {}
    evidence: List[EvidenceItem]
    options: List[PolicyOption]
    policy_bundles: List[PolicyBundle] = []
    risks: List[str]
    citations: List[Citation]


class MemoRequest(BaseModel):
    inputs: AdviceRequest
    advice: Optional[AdviceResponse] = None


class MemoResponse(BaseModel):
    memo_path: str
    memo_markdown: str
