from __future__ import annotations

import re
from datetime import date
from typing import Iterable

from app.models import AdviceResponse

NUMERIC_PATTERN = re.compile(r"\b\d+(?:\.\d+)?%?\b")


def _find_numeric(text: str) -> bool:
    return bool(NUMERIC_PATTERN.search(text))


def _validate_item_has_citations(text: str, citations: Iterable[str], context: str) -> None:
    if _find_numeric(text) and not list(citations):
        raise ValueError(f"Numeric claim without citation in {context}.")


def validate_response_citations(response: AdviceResponse) -> None:
    if not response.citations:
        raise ValueError("Response must include citations.")

    citation_ids = {citation.citation_id for citation in response.citations}
    citation_map = {citation.citation_id: citation for citation in response.citations}
    if len(citation_ids) != len(response.citations):
        raise ValueError("Duplicate citation_id values found.")
    for citation in response.citations:
        if not citation.dataset_id or not citation.url.startswith(("https://", "http://")):
            raise ValueError(f"Invalid citation metadata for {citation.citation_id}.")
        try:
            date.fromisoformat(citation.retrieval_date)
        except ValueError as exc:
            raise ValueError(f"Invalid retrieval_date for {citation.citation_id}.") from exc

    _validate_item_has_citations(response.summary, [], "summary")

    for evidence in response.evidence:
        _validate_item_has_citations(evidence.claim, evidence.citations, f"evidence:{evidence.label}")
        for citation_id in evidence.citations:
            if citation_id not in citation_ids:
                raise ValueError(f"Evidence references unknown citation_id: {citation_id}")
            if _find_numeric(evidence.claim):
                citation = citation_map[citation_id]
                if not citation.geography or not citation.date_range:
                    raise ValueError(f"Numeric evidence lacks geography or date range: {citation_id}")

    for outlook in response.outlook:
        if outlook.predicted_value is not None and (not outlook.citations or not outlook.evaluation_note):
            raise ValueError(f"Forecast without citations: {outlook.metric}")
        if outlook.status == "available" and outlook.predicted_value is None:
            raise ValueError(f"Available forecast has no value: {outlook.metric}")
        for citation_id in outlook.citations:
            if citation_id not in citation_ids:
                raise ValueError(f"Forecast references unknown citation_id: {citation_id}")
            citation = citation_map[citation_id]
            if outlook.predicted_value is not None and (not citation.geography or not citation.date_range):
                raise ValueError(f"Forecast citation lacks geography or date range: {citation_id}")

    for option in response.options:
        _validate_item_has_citations(option.description, [], f"option:{option.title}")
        for bullet in option.pros + option.cons:
            _validate_item_has_citations(bullet, [], f"option:{option.title}")
        _validate_item_has_citations(option.implementation_notes, [], f"option:{option.title}")
        if "heuristic" not in option.scoring_note.lower():
            raise ValueError(f"Policy option lacks a heuristic-scoring disclaimer: {option.title}")

    for bundle in response.policy_bundles:
        if "heuristic" not in bundle.scoring_note.lower():
            raise ValueError(f"Policy bundle lacks a heuristic-scoring disclaimer: {bundle.name}")

    for risk in response.risks:
        _validate_item_has_citations(risk, [], "risk")
