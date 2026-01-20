from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from app.core.policy_lens import rank_options
from app.data.registry import get_dataset_metadata
from app.models import AdviceRequest, AdviceResponse, Citation, EvidenceItem, PolicyOption
from app.services.policy_library import get_policy_options

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"


def _load_processed(dataset_id: str, filename: str) -> pd.DataFrame:
    processed_path = DATA_DIR / "processed" / dataset_id / filename
    if not processed_path.exists():
        fixture_path = DATA_DIR / "fixtures" / dataset_id / filename
        if fixture_path.exists():
            processed_path.parent.mkdir(parents=True, exist_ok=True)
            processed_path.write_text(fixture_path.read_text())
    if processed_path.exists():
        return pd.read_csv(processed_path)
    return pd.DataFrame()


def _citation_for(dataset_id: str) -> Citation:
    metadata = get_dataset_metadata(dataset_id)
    return Citation(
        citation_id=dataset_id,
        dataset_id=dataset_id,
        url=metadata["url"],
        retrieval_date=metadata["retrieval_date"],
        note=metadata.get("name"),
    )


def _format_currency(value: float) -> str:
    return f"${value:,.0f}"


def build_evidence(request: AdviceRequest) -> List[EvidenceItem]:
    evidence: List[EvidenceItem] = []
    geography = request.geography
    issue_area = request.issue_area
    if issue_area not in {"labor_market", "housing", "fiscal", "general"}:
        issue_area = "general"

    if issue_area in ("labor_market", "general"):
        bls = _load_processed("bls_unemployment", "unemployment.csv")
        if not bls.empty:
            latest = bls.sort_values("date").iloc[-1]
            claim = (
                f"Florida unemployment rate was {latest['value']:.1f}% in {latest['date']}."
            )
            evidence.append(EvidenceItem(
                label="Unemployment rate",
                claim=claim,
                citations=["bls_unemployment"],
            ))
        fred = _load_processed("fred_macro", "fred_macro.csv")
        if not fred.empty:
            series = fred[fred["series_id"] == "FLNGSP"]
            if not series.empty:
                latest = series.sort_values("date").iloc[-1]
                claim = (
                    f"Florida real GDP was {latest['value']:,.0f} in {latest['date']}."
                )
                evidence.append(EvidenceItem(
                    label="State output",
                    claim=claim,
                    citations=["fred_macro"],
                ))

    if issue_area in ("housing", "general"):
        acs = _load_processed("census_acs_fl_county", "acs_county.csv")
        if not acs.empty:
            row = None
            if geography.level == "county":
                if geography.value.isdigit():
                    match = acs[acs["county_fips"] == geography.value]
                    if not match.empty:
                        row = match.iloc[0]
                if row is None:
                    match = acs[acs["county_name"].str.contains(geography.value, case=False, na=False)]
                    if not match.empty:
                        row = match.iloc[0]
            if row is None:
                row = acs.iloc[0]
            claim = (
                f"Median household income in {row['county_name']} was {_format_currency(row['median_household_income'])}, "
                f"and median gross rent was {_format_currency(row['median_gross_rent'])}."
            )
            evidence.append(EvidenceItem(
                label="Income and rent",
                claim=claim,
                citations=["census_acs_fl_county"],
            ))
            claim = (
                f"The estimated poverty rate in {row['county_name']} was {row['poverty_rate'] * 100:.1f}%."
            )
            evidence.append(EvidenceItem(
                label="Poverty rate",
                claim=claim,
                citations=["census_acs_fl_county"],
            ))

    if issue_area in ("fiscal",):
        fred = _load_processed("fred_macro", "fred_macro.csv")
        if not fred.empty:
            series = fred[fred["series_id"] == "FLUR"]
            if not series.empty:
                latest = series.sort_values("date").iloc[-1]
                claim = (
                    f"FRED reports Florida unemployment rate at {latest['value']:.1f}% in {latest['date']}."
                )
                evidence.append(EvidenceItem(
                    label="Labor market baseline",
                    claim=claim,
                    citations=["fred_macro"],
                ))

    return evidence


def generate_summary(issue_area: str) -> str:
    if issue_area == "housing":
        return "Evidence indicates affordability pressures that warrant targeted, balanced responses."
    if issue_area == "labor_market":
        return "Evidence indicates labor market conditions that merit near-term monitoring and targeted actions."
    if issue_area == "fiscal":
        return "Evidence suggests aligning fiscal choices with current macroeconomic conditions."
    return "Evidence indicates mixed conditions; prioritize actions based on local constraints."


def generate_risks(issue_area: str) -> List[str]:
    return [
        "Short-term actions may not address longer-term structural constraints.",
        "Capacity limitations could slow implementation without coordinated partners.",
        "Data is subject to revision; monitor updates during implementation.",
    ]


def generate_options(issue_area: str, policy_lens: str, budget_sensitivity: float) -> List[PolicyOption]:
    options = get_policy_options(issue_area)
    ranked = rank_options(options, policy_lens, budget_sensitivity)
    formatted = []
    for option in ranked[:5]:
        formatted.append(PolicyOption(
            title=option["title"],
            description=option["description"],
            pros=[option["pros"]],
            cons=[option["cons"]],
            implementation_notes=option["implementation_notes"],
        ))
    return formatted


def build_citations(evidence: List[EvidenceItem]) -> List[Citation]:
    dataset_ids = {citation_id for item in evidence for citation_id in item.citations}
    return [_citation_for(dataset_id) for dataset_id in dataset_ids]


def generate_advice(request: AdviceRequest) -> AdviceResponse:
    evidence = build_evidence(request)
    citations = build_citations(evidence)
    response = AdviceResponse(
        summary=generate_summary(request.issue_area),
        evidence=evidence,
        options=generate_options(request.issue_area, request.policy_lens, request.budget_sensitivity),
        risks=generate_risks(request.issue_area),
        citations=citations,
    )
    return response
