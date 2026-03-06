from __future__ import annotations

from tool_finder.schemas import EvaluatedCandidate


def build_explanation(item: EvaluatedCandidate) -> str:
    return (
        f"{item.candidate.vendor}: match={item.match_type.value}, "
        f"deadline={item.deadline_status.value if item.deadline_status else 'unknown'}, "
        f"unit_cost={item.effective_unit_cost}, trust={item.trust_tier.value}."
    )
