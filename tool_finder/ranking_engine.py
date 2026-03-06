from __future__ import annotations

from collections import defaultdict

from tool_finder.schemas import DeadlineStatus, EvaluatedCandidate, MatchType, RankedResults, TrustTier
from tool_finder.vendor_trust import low_trust_override_allowed

_MATCH_RANK = {
    MatchType.EXACT_OEM: 0,
    MatchType.EXACT_SPEC: 1,
    MatchType.SUBSTITUTE: 2,
    MatchType.LOW_CONFIDENCE: 3,
}

_TRUST_RANK = {TrustTier.HIGH: 0, TrustTier.MEDIUM: 1, TrustTier.LOW: 2}


def _base_sort_key(item: EvaluatedCandidate):
    arrival = item.candidate.availability.estimated_arrival_date if item.candidate.availability else None
    return (
        _MATCH_RANK[item.match_type],
        item.effective_unit_cost if item.effective_unit_cost is not None else float("inf"),
        _TRUST_RANK[item.trust_tier],
        arrival,
    )


def _apply_trust_override(items: list[EvaluatedCandidate]) -> list[EvaluatedCandidate]:
    by_signature: dict[tuple, list[EvaluatedCandidate]] = defaultdict(list)
    for i in items:
        signature = (
            i.match_type,
            i.deadline_status,
        )
        by_signature[signature].append(i)

    output: list[EvaluatedCandidate] = []
    for group in by_signature.values():
        highs = [i for i in group if i.trust_tier != TrustTier.LOW and i.effective_unit_cost is not None]
        lows = [i for i in group if i.trust_tier == TrustTier.LOW and i.effective_unit_cost is not None]
        if highs and lows:
            best_high = min(highs, key=lambda x: x.effective_unit_cost)
            for low in lows:
                if not low_trust_override_allowed(low.effective_unit_cost, best_high.effective_unit_cost):
                    low.effective_unit_cost += 10_000
        output.extend(group)
    return output


def rank_results(items: list[EvaluatedCandidate]) -> RankedResults:
    adjusted = _apply_trust_override(items)
    feasible = [i for i in adjusted if i.deadline_status in {None, DeadlineStatus.DEADLINE_FEASIBLE}]
    missed = [i for i in adjusted if i.deadline_status in {DeadlineStatus.SLIGHT_MISS, DeadlineStatus.FUTURE_OPTION_ONLY}]

    feasible.sort(key=_base_sort_key)
    missed.sort(
        key=lambda i: (
            0 if i.deadline_status == DeadlineStatus.SLIGHT_MISS else 1,
            *_base_sort_key(i),
        )
    )
    return RankedResults(deadline_feasible_results=feasible, missed_deadline_results=missed)
