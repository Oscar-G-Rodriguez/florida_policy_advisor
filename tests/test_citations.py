import pytest

from app.core.citations import validate_response_citations
from app.models import AdviceResponse, Citation, EvidenceItem, PolicyOption


def test_citation_validator_rejects_uncited_numeric():
    response = AdviceResponse(
        summary="No numbers here.",
        evidence=[
            EvidenceItem(
                label="Test",
                claim="Unemployment rate was 3.1%.",
                citations=[],
            )
        ],
        options=[
            PolicyOption(
                title="Option",
                description="Neutral option.",
                pros=["Stable rollout."],
                cons=["Requires coordination."],
                implementation_notes="Use existing channels.",
            )
        ],
        risks=["Data revisions may occur."],
        citations=[
            Citation(
                citation_id="bls_unemployment",
                dataset_id="bls_unemployment",
                url="https://api.bls.gov/publicAPI/v2/timeseries/data/",
                retrieval_date="2026-01-15",
            )
        ],
    )

    with pytest.raises(ValueError):
        validate_response_citations(response)
