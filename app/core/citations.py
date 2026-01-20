from __future__ import annotations

import re
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
    if len(citation_ids) != len(response.citations):
        raise ValueError("Duplicate citation_id values found.")

    _validate_item_has_citations(response.summary, [], "summary")

    for evidence in response.evidence:
        _validate_item_has_citations(evidence.claim, evidence.citations, f"evidence:{evidence.label}")
        for citation_id in evidence.citations:
            if citation_id not in citation_ids:
                raise ValueError(f"Evidence references unknown citation_id: {citation_id}")

    for outlook in response.outlook:
        if outlook.predicted_value is not None and not outlook.citations:
            raise ValueError(f"Forecast without citations: {outlook.metric}")
        for citation_id in outlook.citations:
            if citation_id not in citation_ids:
                raise ValueError(f"Forecast references unknown citation_id: {citation_id}")

    for option in response.options:
        _validate_item_has_citations(option.description, [], f"option:{option.title}")
        for bullet in option.pros + option.cons:
            _validate_item_has_citations(bullet, [], f"option:{option.title}")
        _validate_item_has_citations(option.implementation_notes, [], f"option:{option.title}")

    for risk in response.risks:
        _validate_item_has_citations(risk, [], "risk")
