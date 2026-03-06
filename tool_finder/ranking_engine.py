from __future__ import annotations

from datetime import date

from .cost_engine import compute_delivered_total, compute_effective_unit_cost
from .deadline_engine import classify_deadline
from .match_engine import classify_match
from .schemas import Candidate, DeadlineStatus, MatchType, RankedResult, RankingOutput, SourceRequest
from .vendor_trust import low_trust_override_applies, trust_score

MATCH_CLASS_ORDER = {
    MatchType.EXACT_OEM: 0,
    MatchType.EXACT_SPEC: 1,
    MatchType.SUBSTITUTE: 2,
    MatchType.LOW_CONFIDENCE: 3,
}

DEADLINE_ORDER = {
    DeadlineStatus.DEADLINE_FEASIBLE: 0,
    DeadlineStatus.SLIGHT_MISS: 1,
    DeadlineStatus.FUTURE_OPTION_ONLY: 2,
}


def _arrival_date(candidate: Candidate) -> date:
    if candidate.availability and candidate.availability.estimated_arrival_date:
        return candidate.availability.estimated_arrival_date
    return date.max


def rank_candidates(source_profile, source_request: SourceRequest, candidates: list[Candidate]) -> RankingOutput:
    ranked: list[RankedResult] = []
    today = source_request.today or date.today()

    for candidate in candidates:
        match_type, matched_fields, missing_fields = classify_match(
            source_profile,
            candidate.attributes,
            source_request.match_mode,
        )
        delivered_total = compute_delivered_total(candidate)
        unit_cost = compute_effective_unit_cost(candidate, source_request.requested_quantity)
        deadline_status = DeadlineStatus.FUTURE_OPTION_ONLY
        if source_request.needed_by_date and candidate.availability and candidate.availability.estimated_arrival_date:
            deadline_status = classify_deadline(
                today=today,
                needed_by_date=source_request.needed_by_date,
                candidate_arrival_date=candidate.availability.estimated_arrival_date,
            )

        ranked.append(
            RankedResult(
                candidate=candidate,
                match_type=match_type,
                deadline_status=deadline_status,
                delivered_total=delivered_total,
                effective_unit_cost=unit_cost,
                trust_score=trust_score(candidate.trust_tier),
                matched_fields=matched_fields,
                missing_or_unverified_fields=missing_fields,
                explanation=(
                    f"{match_type.value}; {deadline_status.value}; unit_cost={unit_cost:.4f}; trust={candidate.trust_tier}"
                ),
            )
        )

    feasible = [r for r in ranked if r.deadline_status == DeadlineStatus.DEADLINE_FEASIBLE]
    missed = [r for r in ranked if r.deadline_status != DeadlineStatus.DEADLINE_FEASIBLE]

    _apply_trust_overrides(feasible, allow_uniquely_meets_deadline=True)
    _apply_trust_overrides(missed, allow_uniquely_meets_deadline=False)

    feasible.sort(key=_feasible_sort_key)
    missed.sort(key=_missed_sort_key)

    return RankingOutput(deadline_feasible_results=feasible, missed_deadline_results=missed)


def _feasible_sort_key(result: RankedResult):
    trust_penalty = 0
    if result.trust_score == 1 and not result.trust_override_applied:
        trust_penalty = 1000
    return (
        MATCH_CLASS_ORDER[result.match_type],
        result.effective_unit_cost + trust_penalty,
        -result.trust_score,
        _arrival_date(result.candidate),
    )


def _missed_sort_key(result: RankedResult):
    trust_penalty = 0
    if result.trust_score == 1 and not result.trust_override_applied:
        trust_penalty = 1000
    return (
        DEADLINE_ORDER[result.deadline_status],
        MATCH_CLASS_ORDER[result.match_type],
        result.effective_unit_cost + trust_penalty,
        -result.trust_score,
        _arrival_date(result.candidate),
    )


def _apply_trust_overrides(results: list[RankedResult], allow_uniquely_meets_deadline: bool) -> None:
    if not results:
        return

    higher_trust_costs = [r.effective_unit_cost for r in results if r.trust_score > 1]
    reference_cost = min(higher_trust_costs) if higher_trust_costs else 0.0

    for result in results:
        if result.trust_score > 1:
            continue
        uniquely_meets_deadline = allow_uniquely_meets_deadline and not higher_trust_costs
        result.trust_override_applied = low_trust_override_applies(
            low_trust_unit_cost=result.effective_unit_cost,
            reference_higher_trust_unit_cost=reference_cost,
            uniquely_meets_deadline=uniquely_meets_deadline,
        )
