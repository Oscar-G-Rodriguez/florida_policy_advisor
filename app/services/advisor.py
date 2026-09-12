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


def _citation_for(dataset_id: str, request: AdviceRequest) -> Citation:
    metadata = get_dataset_metadata(dataset_id)
    if dataset_id == "bls_unemployment":
        frame, date_column, geography = _load_processed(dataset_id, "unemployment.csv"), "date", "Florida"
    elif dataset_id == "fred_macro":
        frame, date_column, geography = _load_processed(dataset_id, "fred_macro.csv"), "date", "Florida"
    else:
        frame, date_column, geography = _load_processed(dataset_id, "acs_county.csv"), "year", (request.geography.value if request.geography.level == "county" else "Florida")
    date_range = None
    if not frame.empty and date_column in frame:
        values = frame[date_column].dropna().astype(str)
        if not values.empty:
            date_range = f"{values.min()} to {values.max()}"
    return Citation(
        citation_id=dataset_id,
        dataset_id=dataset_id,
        url=metadata["url"],
        retrieval_date=metadata["retrieval_date"],
        note=metadata.get("name"),
        data_mode=metadata.get("data_mode", "unknown"),
        geography=geography,
        date_range=date_range,
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
    if geography.level == "state" and acs["county_fips"].nunique() < 67:
        return None
    numeric_cols = acs.select_dtypes(include="number").columns
    if not numeric_cols.empty:
        weights = pd.to_numeric(acs.get("population"), errors="coerce").fillna(0)
        if weights.sum() <= 0:
            return None
        averaged = {}
        for column in numeric_cols:
            values = pd.to_numeric(acs[column], errors="coerce")
            usable = values.notna() & weights.gt(0)
            averaged[column] = float((values[usable] * weights[usable]).sum() / weights[usable].sum()) if usable.any() else None
        averaged["county_name"] = "Florida (population-weighted county estimate)"
        averaged["county_fips"] = "12"
        return pd.Series(averaged)
    return None


def build_evidence(request: AdviceRequest) -> List[EvidenceItem]:
    evidence: List[EvidenceItem] = []
    geography = request.geography
    issue_area = request.issue_area
    include_all = issue_area == "all"
    if include_all or issue_area == "labor_market":
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
    if include_all or issue_area == "housing":
        acs = _load_processed("census_acs_fl_county", "acs_county.csv")
        if not acs.empty:
            row = _select_acs_row(acs, geography)
            if row is None:
                return evidence
            claim = f"Median household income in {row['county_name']} was {_format_currency(row['median_household_income'])}, and median gross rent was {_format_currency(row['median_gross_rent'])}."
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
    if include_all or issue_area == "fiscal":
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
    return "This request is outside the supported scope."


def generate_risks(issue_area: str) -> List[str]:
    return [
        "Short-term actions may not address longer-term structural constraints.",
        "Capacity limitations could slow implementation without coordinated partners.",
        "Data is subject to revision; monitor updates during implementation.",
        "Forecasts are evaluated statistical baselines, not estimates of policy impact or causal effects.",
        "Policy scores and impact weights are heuristic prioritization inputs, not empirical effect sizes.",
    ]


def build_citations(request: AdviceRequest, evidence: List[EvidenceItem], outlook: List[ForecastItem]) -> List[Citation]:
    dataset_ids = {citation_id for item in evidence for citation_id in item.citations}
    dataset_ids.update({citation_id for item in outlook for citation_id in item.citations})
    return [_citation_for(dataset_id, request) for dataset_id in sorted(dataset_ids)]


def _data_mode(citations: List[Citation]) -> tuple[str, str]:
    modes = {citation.data_mode for citation in citations}
    if not citations or modes == {"unknown"}:
        return "unknown", "Data provenance is incomplete. Refresh supported datasets before relying on this output."
    if modes == {"live"}:
        return "live", "Live API data was used. Review each citation's geography, date range, and retrieval date."
    if modes == {"fixture"}:
        return "fixture", "OFFLINE FIXTURE DATA: this output uses packaged sample data, not a live API refresh. Do not treat it as current analysis."
    return "mixed", "MIXED DATA MODES: some results use offline fixtures or have unknown provenance. Review citations before use."


def generate_advice(request: AdviceRequest) -> AdviceResponse:
    evidence = build_evidence(request)
    outlook, outlook_summary, urgency, forecast_info = generate_outlook(request)
    citations = build_citations(request, evidence, outlook)
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
        data_mode=_data_mode(citations)[0],
        data_notice=_data_mode(citations)[1],
    )
    return response
