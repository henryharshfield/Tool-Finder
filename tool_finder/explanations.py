from __future__ import annotations

from tool_finder.schemas import EvaluatedCandidate


def build_explanation(item: EvaluatedCandidate) -> str:
    penalty_note = ""
    if item.ranking_penalty:
        penalty_note = " trust_penalty_applied_for_ranking=true"

    missing_note = ""
    if item.missing_or_unverified_fields:
        missing_note = f" missing_or_unverified={item.missing_or_unverified_fields}"

    return (
        f"{item.candidate.vendor}: match={item.match_type.value}, "
        f"deadline={item.deadline_status.value if item.deadline_status else 'unknown'}, "
        f"effective_unit_cost={item.effective_unit_cost}, trust={item.trust_tier.value}."
        f"{missing_note}{penalty_note}"
    )
