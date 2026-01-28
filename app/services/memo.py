from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Tuple

from app.models import AdviceRequest, AdviceResponse

ROOT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT_DIR / "outputs" / "memos"


def _format_budget(budget_sensitivity: float) -> str:
    if budget_sensitivity >= 0.67:
        return "high"
    if budget_sensitivity >= 0.34:
        return "medium"
    return "low"


def _format_geography(geography) -> str:
    if geography.level == "state":
        return "State of Florida"
    return geography.value


def render_memo(request: AdviceRequest, advice: AdviceResponse) -> str:
    memo_lines = [
        "# Florida Policy Advisor Memo",
        "",
        "Date: generated on request",
        "",
        "## Request",
        f"- Issue area: {request.issue_area}",
        f"- Geography: {_format_geography(request.geography)}",
        f"- Time horizon: {request.time_horizon}",
        f"- Budget sensitivity: {_format_budget(request.budget_sensitivity)}",
        f"- Policy lens: {request.policy_lens}",
    ]
    if advice.objectives:
        memo_lines.append("- Objectives:")
        for sector, objective in advice.objectives.items():
            memo_lines.append(f"  - {sector}: {objective}")

    memo_lines.extend([
        "",
        "## Executive summary",
        advice.summary,
        "",
        "## Evidence",
    ])

    for item in advice.evidence:
        citations = " ".join([f"[^{citation_id}]" for citation_id in item.citations])
        memo_lines.append(f"- {item.claim} {citations}")

    memo_lines.extend([
        "",
        "## Policy options (ranked)",
    ])
    for option in advice.options:
        memo_lines.append(f"### {option.title}")
        memo_lines.append(option.description)
        memo_lines.append("- Pros: " + "; ".join(option.pros))
        memo_lines.append("- Cons: " + "; ".join(option.cons))
        memo_lines.append(f"- Implementation notes: {option.implementation_notes}")
        memo_lines.append("")

    memo_lines.append("## Risks and considerations")
    for risk in advice.risks:
        memo_lines.append(f"- {risk}")

    if advice.policy_bundles:
        memo_lines.append("")
        memo_lines.append("## Recommended policy bundles")
        for bundle in advice.policy_bundles:
            memo_lines.append(f"### {bundle.name}")
            memo_lines.append(f"- Score: {bundle.score}")
            memo_lines.append(f"- Rationale: {bundle.rationale}")
            if bundle.tradeoffs:
                memo_lines.append(f"- Tradeoffs: {', '.join(bundle.tradeoffs)}")
            memo_lines.append("")

    memo_lines.append("")
    memo_lines.append("## Outlook")
    if advice.outlook_summary:
        memo_lines.append(advice.outlook_summary)
        memo_lines.append("")
    if advice.outlook:
        for item in advice.outlook:
            citations = " ".join([f"[^{citation_id}]" for citation_id in item.citations])
            unit = f" {item.unit}" if item.unit else ""
            if item.predicted_value is None:
                suffix = f" {citations}".rstrip()
                memo_lines.append(
                    f"- {item.metric} ({item.sector}, {item.horizon}): "
                    f"No data available yet.{suffix}"
                )
            else:
                memo_lines.append(
                    f"- {item.metric} ({item.sector}, {item.horizon}): "
                    f"{item.predicted_value:.2f}{unit} ({item.direction}). {citations}"
                )
    if advice.forecast_info:
        memo_lines.append("")
        memo_lines.append(f"Forecast info: {advice.forecast_info}")

    memo_lines.append("")
    memo_lines.append("## Citations")
    for citation in advice.citations:
        memo_lines.append(
            f"[^{citation.citation_id}]: {citation.dataset_id} | {citation.url} | retrieved {citation.retrieval_date}"
        )

    return "\n".join(memo_lines).strip() + "\n"


def save_memo(request: AdviceRequest, advice: AdviceResponse) -> Tuple[str, str]:
    memo_markdown = render_memo(request, advice)
    digest = hashlib.sha256(memo_markdown.encode("utf-8")).hexdigest()[:8]
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    folder = OUTPUT_DIR / f"{timestamp}_{digest}"
    folder.mkdir(parents=True, exist_ok=True)
    memo_path = folder / "memo.md"
    memo_path.write_text(memo_markdown)
    return str(memo_path), memo_markdown
