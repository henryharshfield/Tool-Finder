from __future__ import annotations

import json
from pathlib import Path

from tool_finder.deadline_engine import classify_deadline
from tool_finder.ontology.fasteners import is_supported_fastener_family
from tool_finder.service import evaluate_candidates, source_request_from_dict
from tool_finder.vendor_trust import low_trust_override_allowed

FIXTURES = Path("fixtures")


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_ontology_supported_family():
    assert is_supported_fastener_family("bolts")
    assert not is_supported_fastener_family("bearing")


def test_metric_imperial_non_equivalence_fixture_2():
    fixture = load_fixture("fastener_fixture_2.json")
    req = source_request_from_dict({"requested_quantity": 10, "match_mode": "exact_only"})
    ranked = evaluate_candidates(req, fixture["source_profile"], [fixture["candidate"]])
    candidate = ranked.deadline_feasible_results + ranked.missed_deadline_results
    assert candidate[0].match_type.value != "exact_spec"


def test_deadline_125_percent_rule_fixture_3():
    fixture = load_fixture("fastener_fixture_3.json")
    req = source_request_from_dict(fixture["source_request"])

    raw_candidates = []
    for c in fixture["candidates"]:
        raw_candidates.append(
            {
                "vendor": c["vendor"],
                "attributes": {
                    "fastener_family": "bolt",
                    "nominal_unit_system": "imperial",
                    "diameter": "1/4 in",
                    "thread_standard": "UNC",
                    "thread_pitch_tpi": 20,
                    "length": "1 in",
                    "material_family": "steel",
                },
                "pricing": {"item_total": 10.0, "shipping": 0.0, "fees": 0.0},
                "availability": {"estimated_arrival_date": c["estimated_arrival_date"]},
            }
        )

    ranked = evaluate_candidates(req, {
        "fastener_family": "bolt",
        "nominal_unit_system": "imperial",
        "diameter": "1/4 in",
        "thread_standard": "UNC",
        "thread_pitch_tpi": 20,
        "length": "1 in",
        "material_family": "steel",
    }, raw_candidates)

    statuses = {
        item.candidate.vendor: item.deadline_status.value
        for item in ranked.deadline_feasible_results + ranked.missed_deadline_results
    }
    assert statuses == fixture["expected_behavior"]


def test_moq_requested_quantity_cost_fixture_5():
    fixture = load_fixture("fastener_fixture_5.json")
    req = source_request_from_dict(fixture["source_request"])
    source_profile = {
        "fastener_family": "bolt",
        "nominal_unit_system": "imperial",
        "diameter": "1/4 in",
        "thread_standard": "UNC",
        "thread_pitch_tpi": 20,
        "length": "1 in",
        "material_family": "steel",
    }
    raw_candidates = [
        {
            "vendor": c["vendor"],
            "moq": c["moq"],
            "attributes": source_profile,
            "pricing": {"item_total": c["delivered_total"], "shipping": 0.0, "fees": 0.0},
            "availability": {"estimated_arrival_date": "2026-03-02"},
            "trust_tier": "High",
        }
        for c in fixture["candidates"]
    ]
    req.today = req.today or __import__("datetime").date(2026, 3, 1)
    req.needed_by_date = req.needed_by_date or __import__("datetime").date(2026, 3, 10)
    ranked = evaluate_candidates(req, source_profile, raw_candidates)

    feasible = ranked.deadline_feasible_results
    unit_costs = {i.candidate.vendor: i.effective_unit_cost for i in feasible}
    assert unit_costs["MOQ10"] == fixture["expected_behavior"]["MOQ10_effective_unit_cost"]
    assert unit_costs["MOQ6"] == fixture["expected_behavior"]["MOQ6_effective_unit_cost"]
    assert feasible[0].candidate.vendor == fixture["expected_behavior"]["top_result_vendor"]


def test_trust_override_threshold_fixture_4():
    fixture = load_fixture("fastener_fixture_4.json")
    high = next(c for c in fixture["evaluated_candidates"] if c["vendor"] == "HighTrust")
    low_15 = next(c for c in fixture["evaluated_candidates"] if c["vendor"] == "LowTrust15PctCheaper")
    low_27 = next(c for c in fixture["evaluated_candidates"] if c["vendor"] == "LowTrust27PctCheaper")

    assert not low_trust_override_allowed(low_15["effective_unit_cost"], high["effective_unit_cost"])
    assert low_trust_override_allowed(low_27["effective_unit_cost"], high["effective_unit_cost"])


def test_fixture_1_ranking_prefers_delivered_cost_over_faster_arrival():
    fixture = load_fixture("fastener_fixture_1.json")
    req = source_request_from_dict(fixture["source_request"])
    req.today = __import__("datetime").date(2026, 3, 1)
    ranked = evaluate_candidates(req, fixture["source_profile"], fixture["candidates"])
    assert ranked.deadline_feasible_results[0].candidate.vendor == fixture["expected_behavior"]["top_result_vendor"]
