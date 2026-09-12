from app.models import AdviceRequest
from app.services.advisor import generate_advice
from app.services.memo import render_memo


def test_memo_preserves_fixture_and_heuristic_disclaimers():
    request = AdviceRequest(
        issue_area="housing",
        geography={"level": "county", "value": "Miami-Dade County"},
        time_horizon="near_term",
        budget_sensitivity=0.5,
        policy_lens="equity",
    )
    memo = render_memo(request, generate_advice(request))
    assert "OFFLINE FIXTURE DATA" in memo
    assert "heuristic prioritization aids" in memo
    assert "## Citations" in memo
