from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from app.data.registry import get_dataset_metadata
from app.models import AdviceRequest, AdviceResponse, Citation, EvidenceItem, ForecastItem
from app.services.forecast import generate_outlook
from app.services.policy_engine import rank_policies

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


def _select_acs_row(acs: pd.DataFrame, geography) -> pd.Series | None:
    if acs.empty:
        return None
    if "year" in acs.columns:
        acs = acs.sort_values("year")
        latest_year = acs["year"].iloc[-1]
        acs = acs[acs["year"] == latest_year]
    if geography.level == "county":
        if geography.value.isdigit():
            match = acs[acs["county_fips"] == geography.value]
            if not match.empty:
                return match.iloc[0]
        match = acs[acs["county_name"].str.contains(geography.value, case=False, na=False)]
        if not match.empty:
            return match.iloc[0]
    numeric_cols = acs.select_dtypes(include="number").columns
    if not numeric_cols.empty:
        averages = acs[numeric_cols].mean()
        averaged = averages.to_dict()
        averaged["county_name"] = "Florida (avg)"
        averaged["county_fips"] = "state"
        return pd.Series(averaged)
    return None


def build_evidence(request: AdviceRequest) -> List[EvidenceItem]:
    evidence: List[EvidenceItem] = []
    geography = request.geography
    issue_area = request.issue_area
    include_all = issue_area == "all"
    if issue_area not in {"labor_market", "housing", "fiscal", "general", "all"}:
        issue_area = "general"

    if include_all or issue_area in ("labor_market", "general"):
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

    if include_all or issue_area in ("housing", "general"):
        acs = _load_processed("census_acs_fl_county", "acs_county.csv")
        if not acs.empty:
            row = _select_acs_row(acs, geography)
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
            if "median_home_value" in row:
                claim = (
                    f"Median home value in {row['county_name']} was {_format_currency(row['median_home_value'])}."
                )
                evidence.append(EvidenceItem(
                    label="Home value",
                    claim=claim,
                    citations=["census_acs_fl_county"],
                ))
            if "vacancy_rate" in row:
                claim = (
                    f"Housing vacancy rate in {row['county_name']} was {row['vacancy_rate'] * 100:.1f}%."
                )
                evidence.append(EvidenceItem(
                    label="Vacancy rate",
                    claim=claim,
                    citations=["census_acs_fl_county"],
                ))
            if "rent_to_income" in row:
                claim = (
                    f"Rent-to-income ratio in {row['county_name']} was {row['rent_to_income'] * 100:.1f}%."
                )
                evidence.append(EvidenceItem(
                    label="Rent burden",
                    claim=claim,
                    citations=["census_acs_fl_county"],
                ))
            if "population" in row:
                claim = (
                    f"Estimated population in {row['county_name']} was {int(row['population']):,}."
                )
                evidence.append(EvidenceItem(
                    label="Population",
                    claim=claim,
                    citations=["census_acs_fl_county"],
                ))

    if include_all or issue_area in ("fiscal",):
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
            gdp = fred[fred["series_id"] == "FLNGSP"].sort_values("date")
            if len(gdp) >= 2:
                latest = gdp.iloc[-1]
                prior = gdp.iloc[-2]
                growth = ((latest["value"] - prior["value"]) / prior["value"]) * 100
                claim = (
                    f"Real GDP increased by {growth:.1f}% between {prior['date']} and {latest['date']}."
                )
                evidence.append(EvidenceItem(
                    label="GDP growth",
                    claim=claim,
                    citations=["fred_macro"],
                ))

    return evidence


def generate_summary(issue_area: str) -> str:
    if issue_area == "all":
        return "Evidence indicates cross-sector pressures; a balanced, coordinated portfolio is recommended."
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
        "Forward-looking indicators can shift quickly; revisit the plan as new forecasts arrive.",
    ]


def build_citations(evidence: List[EvidenceItem], outlook: List[ForecastItem]) -> List[Citation]:
    dataset_ids = {citation_id for item in evidence for citation_id in item.citations}
    dataset_ids.update({citation_id for item in outlook for citation_id in item.citations})
    return [_citation_for(dataset_id) for dataset_id in dataset_ids]


def generate_advice(request: AdviceRequest) -> AdviceResponse:
    evidence = build_evidence(request)
    outlook, outlook_summary, urgency, forecast_info = generate_outlook(request)
    citations = build_citations(evidence, outlook)
    options, bundles, objectives = rank_policies(request, outlook, urgency)
    response = AdviceResponse(
        summary=generate_summary(request.issue_area),
        outlook_summary=outlook_summary,
        outlook=outlook,
        forecast_info=forecast_info,
        objectives=objectives,
        evidence=evidence,
        options=options,
        policy_bundles=bundles,
        risks=generate_risks(request.issue_area),
        citations=citations,
    )
    return response
