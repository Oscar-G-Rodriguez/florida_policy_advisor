from __future__ import annotations

from typing import List, Literal, Optional

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


class AdviceResponse(BaseModel):
    summary: str
    evidence: List[EvidenceItem]
    options: List[PolicyOption]
    risks: List[str]
    citations: List[Citation]


class MemoRequest(BaseModel):
    inputs: AdviceRequest
    advice: Optional[AdviceResponse] = None


class MemoResponse(BaseModel):
    memo_path: str
    memo_markdown: str
