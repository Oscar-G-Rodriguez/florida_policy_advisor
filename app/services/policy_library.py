from __future__ import annotations

from typing import List, Dict

POLICY_OPTIONS: List[Dict[str, str]] = [
    {
        "id": "rapid_employer_outreach",
        "title": "Rapid employer outreach and placement support",
        "description": "Coordinate with local employers to identify immediate openings and match job seekers quickly.",
        "pros": "Fast-to-deploy support for displaced workers.",
        "cons": "Relies on near-term labor demand being available.",
        "implementation_notes": "Leverage workforce boards and existing employer networks.",
        "cost": "low",
        "speed": "high",
        "equity": "medium",
        "market": "high",
    },
    {
        "id": "targeted_training",
        "title": "Targeted short-cycle training vouchers",
        "description": "Provide short-cycle training vouchers aligned with in-demand occupations.",
        "pros": "Builds skills aligned to current employer needs.",
        "cons": "Training capacity and completion timelines can vary.",
        "implementation_notes": "Align with regional labor market demand signals.",
        "cost": "medium",
        "speed": "medium",
        "equity": "high",
        "market": "medium",
    },
    {
        "id": "childcare_support",
        "title": "Workforce participation supports",
        "description": "Expand access to supports that reduce barriers to work, such as childcare or transportation assistance.",
        "pros": "Improves participation for lower-income households.",
        "cons": "Requires coordination across agencies.",
        "implementation_notes": "Bundle support with workforce placements.",
        "cost": "high",
        "speed": "medium",
        "equity": "high",
        "market": "medium",
    },
    {
        "id": "business_process_streamlining",
        "title": "Business process streamlining",
        "description": "Simplify or accelerate permitting or compliance processes that slow hiring.",
        "pros": "Reduces time-to-hire for employers.",
        "cons": "Requires careful guardrails to protect worker standards.",
        "implementation_notes": "Pilot in sectors with clear bottlenecks.",
        "cost": "low",
        "speed": "high",
        "equity": "low",
        "market": "high",
    },
    {
        "id": "regional_partnerships",
        "title": "Regional employer partnerships",
        "description": "Formalize regional partnerships to align workforce pipelines with employer needs.",
        "pros": "Builds longer-term alignment across sectors.",
        "cons": "Takes time to formalize agreements.",
        "implementation_notes": "Use existing sector partnerships as anchors.",
        "cost": "medium",
        "speed": "low",
        "equity": "medium",
        "market": "medium",
    },
]


def get_policy_options(issue_area: str) -> List[Dict[str, str]]:
    # For MVP, return the full list; future versions can filter by issue area.
    return POLICY_OPTIONS.copy()
