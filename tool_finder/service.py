from __future__ import annotations

from datetime import date

from tool_finder.cost_engine import delivered_total, effective_unit_cost
from tool_finder.deadline_engine import classify_deadline
from tool_finder.explanations import build_explanation
from tool_finder.match_engine import classify_match
from tool_finder.profile_builder import build_fastener_profile
from tool_finder.ranking_engine import rank_results
from tool_finder.schemas import EvaluatedCandidate, MatchMode, SourceRequest, TrustTier
from tool_finder.supplier_connectors.normalization import normalize_candidate


def source_request_from_dict(data: dict) -> SourceRequest:
    return SourceRequest(
        requested_quantity=int(data["requested_quantity"]),
        needed_by_date=date.fromisoformat(data["needed_by_date"]) if data.get("needed_by_date") else None,
        today=date.fromisoformat(data["today"]) if data.get("today") else None,
        country_filter=data.get("country_filter"),
        shipping_destination=data.get("shipping_destination"),
        match_mode=MatchMode(data.get("match_mode", MatchMode.EXACT_PREFERRED_SUBSTITUTES_ALLOWED.value)),
        input_type=data.get("input_type"),
        raw_input=data.get("raw_input"),
    )


def evaluate_candidates(source_request: SourceRequest, source_profile: dict, raw_candidates: list[dict]):
    profile = build_fastener_profile(source_profile)
    evaluated: list[EvaluatedCandidate] = []

    for raw in raw_candidates:
        candidate = normalize_candidate(raw)

        if source_request.country_filter and candidate.country_of_origin and candidate.country_of_origin != source_request.country_filter:
            continue

        match_type, confidence, matched, missing = classify_match(profile, candidate, source_request.match_mode)

        deadline_status = None
        if source_request.needed_by_date and source_request.today and candidate.availability and candidate.availability.estimated_arrival_date:
            deadline_status = classify_deadline(source_request.today, source_request.needed_by_date, candidate.availability.estimated_arrival_date)

        unit_cost = effective_unit_cost(candidate, source_request)
        total = delivered_total(candidate.pricing) if candidate.pricing else None
        trust = candidate.trust_tier or TrustTier.MEDIUM

        item = EvaluatedCandidate(
            candidate=candidate,
            match_type=match_type,
            confidence=confidence,
            deadline_status=deadline_status,
            delivered_total=total,
            effective_unit_cost=unit_cost,
            trust_tier=trust,
            matched_fields=matched,
            missing_or_unverified_fields=missing,
        )
        evaluated.append(item)

    ranked = rank_results(evaluated)
    for item in ranked.deadline_feasible_results + ranked.missed_deadline_results:
        item.explanation = build_explanation(item)
    return ranked
