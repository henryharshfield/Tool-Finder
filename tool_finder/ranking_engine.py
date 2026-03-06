from __future__ import annotations

from tool_finder.schemas import DeadlineStatus, EvaluatedCandidate, MatchType, RankedResults, TrustTier
from tool_finder.vendor_trust import low_trust_override_allowed

_MATCH_RANK = {
    MatchType.EXACT_OEM: 0,
    MatchType.EXACT_SPEC: 1,
    MatchType.SUBSTITUTE: 2,
    MatchType.LOW_CONFIDENCE: 3,
}

_TRUST_RANK = {TrustTier.HIGH: 0, TrustTier.MEDIUM: 1, TrustTier.LOW: 2}

_TRUST_PENALTY = 10_000.0


def _is_uniquely_deadline_feasible(low_item: EvaluatedCandidate, all_items: list[EvaluatedCandidate]) -> bool:
    if low_item.deadline_status != DeadlineStatus.DEADLINE_FEASIBLE:
        return False
    for other in all_items:
        if other is low_item:
            continue
        if other.match_type != low_item.match_type:
            continue
        if other.trust_tier == TrustTier.LOW:
            continue
        if other.deadline_status == DeadlineStatus.DEADLINE_FEASIBLE:
            return False
    return True


def _apply_trust_penalties(items: list[EvaluatedCandidate]) -> None:
    for item in items:
        item.ranking_penalty = 0.0

    for low in items:
        if low.trust_tier != TrustTier.LOW or low.effective_unit_cost is None:
            continue

        comparable_non_low = [
            x for x in items if x.match_type == low.match_type and x.trust_tier != TrustTier.LOW and x.effective_unit_cost is not None
        ]
        if not comparable_non_low:
            continue

        best_non_low = min(comparable_non_low, key=lambda x: x.effective_unit_cost)
        uniquely_feasible = _is_uniquely_deadline_feasible(low, items)
        if not low_trust_override_allowed(
            low_trust_unit_cost=low.effective_unit_cost,
            high_trust_unit_cost=best_non_low.effective_unit_cost,
            low_trust_uniquely_meets_deadline=uniquely_feasible,
        ):
            low.ranking_penalty = _TRUST_PENALTY


def _sort_key(item: EvaluatedCandidate):
    arrival = item.candidate.availability.estimated_arrival_date if item.candidate.availability else None
    effective_with_penalty = (
        item.effective_unit_cost if item.effective_unit_cost is not None else float("inf")
    ) + item.ranking_penalty
    return (
        _MATCH_RANK[item.match_type],
        effective_with_penalty,
        _TRUST_RANK[item.trust_tier],
        arrival,
    )


def rank_results(items: list[EvaluatedCandidate]) -> RankedResults:
    _apply_trust_penalties(items)

    feasible = [i for i in items if i.deadline_status in {None, DeadlineStatus.DEADLINE_FEASIBLE}]
    missed = [i for i in items if i.deadline_status in {DeadlineStatus.SLIGHT_MISS, DeadlineStatus.FUTURE_OPTION_ONLY}]

    feasible.sort(key=_sort_key)
    missed.sort(
        key=lambda i: (
            0 if i.deadline_status == DeadlineStatus.SLIGHT_MISS else 1,
            *_sort_key(i),
        )
    )
    return RankedResults(deadline_feasible_results=feasible, missed_deadline_results=missed)
