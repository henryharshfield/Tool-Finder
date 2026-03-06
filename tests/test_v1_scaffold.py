from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from tool_finder.cost_engine import compute_effective_unit_cost
from tool_finder.deadline_engine import classify_deadline
from tool_finder.match_engine import classify_match
from tool_finder.ontology import normalize_family
from tool_finder.profile_builder import build_fastener_profile
from tool_finder.ranking_engine import rank_candidates
from tool_finder.schemas import Availability, Candidate, DeadlineStatus, MatchMode, Pricing, SourceRequest

ROOT = Path(__file__).resolve().parents[1]


def load_fixture(name: str) -> dict:
    return json.loads((ROOT / "fixtures" / name).read_text())


def build_candidate(payload: dict) -> Candidate:
    pricing_raw = payload.get("pricing")
    if pricing_raw:
        pricing = Pricing(
            item_total=pricing_raw.get("item_total"),
            shipping=pricing_raw.get("shipping"),
            fees=pricing_raw.get("fees"),
            delivered_total=pricing_raw.get("delivered_total"),
            tariff_status=pricing_raw.get("tariff_status"),
        )
    else:
        pricing = Pricing(delivered_total=payload.get("delivered_total"))

    availability_raw = payload.get("availability")
    arrival_raw = None
    if availability_raw:
        arrival_raw = availability_raw.get("estimated_arrival_date")
    elif payload.get("estimated_arrival_date"):
        arrival_raw = payload["estimated_arrival_date"]

    availability = Availability(
        estimated_arrival_date=date.fromisoformat(arrival_raw) if arrival_raw else None,
        stock_status=(availability_raw or {}).get("stock_status"),
    )

    return Candidate(
        vendor=payload["vendor"],
        trust_tier=payload.get("trust_tier", "Medium"),
        source_tier=payload.get("source_tier"),
        listing_url=payload.get("listing_url"),
        attributes=payload.get("attributes", {}),
        pricing=pricing,
        availability=availability,
        moq=payload.get("moq", 1),
        country_of_origin=payload.get("country_of_origin"),
    )


def test_ontology_classification_supported_family():
    assert normalize_family("bolts") == "bolt"


def test_metric_imperial_non_equivalence_from_fixture_2():
    fixture = load_fixture("fastener_fixture_2.json")
    source = build_fastener_profile(fixture["source_profile"])
    match_type, _, missing = classify_match(source, fixture["candidate"]["attributes"], MatchMode.EXACT_ONLY)
    assert match_type.value == "low_confidence"
    assert "metric_imperial_system_mismatch" in missing


def test_deadline_125_percent_grouping_fixture_3():
    fixture = load_fixture("fastener_fixture_3.json")
    src = fixture["source_request"]
    today = date.fromisoformat(src["today"])
    needed = date.fromisoformat(src["needed_by_date"])

    statuses = {
        candidate["vendor"]: classify_deadline(today, needed, date.fromisoformat(candidate["estimated_arrival_date"]))
        for candidate in fixture["candidates"]
    }
    assert statuses["OnTime"] == DeadlineStatus.DEADLINE_FEASIBLE
    assert statuses["SlightMiss"] == DeadlineStatus.SLIGHT_MISS
    assert statuses["FutureOption"] == DeadlineStatus.FUTURE_OPTION_ONLY


def test_moq_effective_unit_cost_fixture_5():
    fixture = load_fixture("fastener_fixture_5.json")
    requested_quantity = fixture["source_request"]["requested_quantity"]
    moq10 = build_candidate(fixture["candidates"][0])
    moq6 = build_candidate(fixture["candidates"][1])

    assert compute_effective_unit_cost(moq10, requested_quantity) == 5.0
    assert compute_effective_unit_cost(moq6, requested_quantity) == 3.5


def test_trust_override_fixture_4():
    fixture = load_fixture("fastener_fixture_4.json")
    high, low15, low27 = fixture["evaluated_candidates"]

    source = build_fastener_profile(
        {
            "family": "bolt",
            "nominal_unit_system": "imperial",
            "diameter": "1/4 in",
            "thread_standard": "UNC",
            "thread_pitch_tpi": 20,
            "length": "1 in",
            "head_type": "hex",
            "material_family": "steel",
        }
    )
    request = SourceRequest(requested_quantity=1, match_mode=MatchMode.EXACT_ONLY)

    candidates = [
        Candidate(
            vendor=high["vendor"],
            trust_tier=high["trust_tier"],
            attributes=source.__dict__.copy(),
            pricing=Pricing(delivered_total=high["effective_unit_cost"]),
            availability=Availability(),
        ),
        Candidate(
            vendor=low15["vendor"],
            trust_tier=low15["trust_tier"],
            attributes=source.__dict__.copy(),
            pricing=Pricing(delivered_total=low15["effective_unit_cost"]),
            availability=Availability(),
        ),
        Candidate(
            vendor=low27["vendor"],
            trust_tier=low27["trust_tier"],
            attributes=source.__dict__.copy(),
            pricing=Pricing(delivered_total=low27["effective_unit_cost"]),
            availability=Availability(),
        ),
    ]

    output = rank_candidates(source, request, candidates)
    order = [r.candidate.vendor for r in output.missed_deadline_results]
    assert order.index("HighTrust") < order.index("LowTrust15PctCheaper")
    assert order.index("LowTrust27PctCheaper") < order.index("HighTrust")


def test_baseline_ranking_fixture_1_and_grouping():
    fixture = load_fixture("fastener_fixture_1.json")
    source = build_fastener_profile(fixture["source_profile"])
    request = SourceRequest(
        requested_quantity=fixture["source_request"]["requested_quantity"],
        needed_by_date=date.fromisoformat(fixture["source_request"]["needed_by_date"]),
        shipping_destination=fixture["source_request"]["shipping_destination"],
        match_mode=MatchMode(fixture["source_request"]["match_mode"]),
        today=date(2026, 3, 1),
    )
    candidates = [build_candidate(raw) for raw in fixture["candidates"]]

    output = rank_candidates(source, request, candidates)
    assert output.deadline_feasible_results
    assert output.deadline_feasible_results[0].candidate.vendor == fixture["expected_behavior"]["top_result_vendor"]
    assert output.missed_deadline_results == []
