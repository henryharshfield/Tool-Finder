from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from tool_finder.ontology.fasteners import is_supported_fastener_family
from tool_finder.schemas import MatchType
from tool_finder.service import evaluate_candidates, source_request_from_dict
from tool_finder.vendor_trust import low_trust_override_allowed

FIXTURES = Path("fixtures")


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def _base_source_profile() -> dict:
    return {
        "fastener_family": "bolt",
        "nominal_unit_system": "imperial",
        "diameter": "1/4 in",
        "thread_standard": "UNC",
        "thread_pitch_tpi": 20,
        "length": "1 in",
        "material_family": "steel",
    }


def test_ontology_supported_family():
    assert is_supported_fastener_family("bolts")
    assert not is_supported_fastener_family("bearing")


def test_metric_imperial_non_equivalence_fixture_2():
    fixture = load_fixture("fastener_fixture_2.json")
    req = source_request_from_dict({"requested_quantity": 10, "match_mode": "exact_only"})
    ranked = evaluate_candidates(req, fixture["source_profile"], [fixture["candidate"]])
    candidate = (ranked.deadline_feasible_results + ranked.missed_deadline_results)[0]

    assert candidate.match_type != MatchType.EXACT_SPEC
    assert "nominal_unit_system" in candidate.missing_or_unverified_fields
    assert "nominal_unit_system" in candidate.explanation


def test_deadline_125_percent_rule_fixture_3():
    fixture = load_fixture("fastener_fixture_3.json")
    req = source_request_from_dict(fixture["source_request"])

    raw_candidates = []
    for c in fixture["candidates"]:
        raw_candidates.append(
            {
                "vendor": c["vendor"],
                "attributes": _base_source_profile(),
                "pricing": {"item_total": 10.0, "shipping": 0.0, "fees": 0.0},
                "availability": {"estimated_arrival_date": c["estimated_arrival_date"]},
            }
        )

    ranked = evaluate_candidates(req, _base_source_profile(), raw_candidates)
    statuses = {
        item.candidate.vendor: item.deadline_status.value
        for item in ranked.deadline_feasible_results + ranked.missed_deadline_results
    }
    assert statuses == fixture["expected_behavior"]


def test_moq_requested_quantity_cost_fixture_5():
    fixture = load_fixture("fastener_fixture_5.json")
    req = source_request_from_dict(fixture["source_request"])
    raw_candidates = [
        {
            "vendor": c["vendor"],
            "moq": c["moq"],
            "attributes": _base_source_profile(),
            "pricing": {"item_total": c["delivered_total"], "shipping": 0.0, "fees": 0.0},
            "availability": {"estimated_arrival_date": "2026-03-02"},
            "trust_tier": "High",
        }
        for c in fixture["candidates"]
    ]
    req.today = date(2026, 3, 1)
    req.needed_by_date = date(2026, 3, 10)

    ranked = evaluate_candidates(req, _base_source_profile(), raw_candidates)
    feasible = ranked.deadline_feasible_results
    unit_costs = {i.candidate.vendor: i.effective_unit_cost for i in feasible}
    assert unit_costs["MOQ10"] == fixture["expected_behavior"]["MOQ10_effective_unit_cost"]
    assert unit_costs["MOQ6"] == fixture["expected_behavior"]["MOQ6_effective_unit_cost"]
    assert feasible[0].candidate.vendor == fixture["expected_behavior"]["top_result_vendor"]


def test_trust_override_threshold_helper_fixture_4():
    fixture = load_fixture("fastener_fixture_4.json")
    high = next(c for c in fixture["evaluated_candidates"] if c["vendor"] == "HighTrust")
    low_15 = next(c for c in fixture["evaluated_candidates"] if c["vendor"] == "LowTrust15PctCheaper")
    low_27 = next(c for c in fixture["evaluated_candidates"] if c["vendor"] == "LowTrust27PctCheaper")

    assert not low_trust_override_allowed(low_15["effective_unit_cost"], high["effective_unit_cost"])
    assert low_trust_override_allowed(low_27["effective_unit_cost"], high["effective_unit_cost"])


def test_low_trust_penalty_does_not_leak_into_business_cost_values():
    req = source_request_from_dict(
        {
            "requested_quantity": 10,
            "today": "2026-03-01",
            "needed_by_date": "2026-03-10",
            "match_mode": "exact_only",
        }
    )
    candidates = [
        {
            "vendor": "HighTrust",
            "trust_tier": "High",
            "attributes": _base_source_profile(),
            "pricing": {"item_total": 40.0, "shipping": 0.0, "fees": 0.0},
            "availability": {"estimated_arrival_date": "2026-03-03"},
        },
        {
            "vendor": "LowTrust15Pct",
            "trust_tier": "Low",
            "attributes": _base_source_profile(),
            "pricing": {"item_total": 34.0, "shipping": 0.0, "fees": 0.0},
            "availability": {"estimated_arrival_date": "2026-03-03"},
        },
        {
            "vendor": "LowTrust27Pct",
            "trust_tier": "Low",
            "attributes": _base_source_profile(),
            "pricing": {"item_total": 29.0, "shipping": 0.0, "fees": 0.0},
            "availability": {"estimated_arrival_date": "2026-03-03"},
        },
    ]

    ranked = evaluate_candidates(req, _base_source_profile(), candidates)
    feasible = ranked.deadline_feasible_results
    by_vendor = {x.candidate.vendor: x for x in feasible}

    # business value must stay unmodified
    assert by_vendor["LowTrust15Pct"].effective_unit_cost == 3.4
    assert by_vendor["LowTrust27Pct"].effective_unit_cost == 2.9

    # ordering behavior: low trust 15% should not beat high trust; 27% may beat
    order = [x.candidate.vendor for x in feasible]
    assert order.index("HighTrust") < order.index("LowTrust15Pct")
    assert order.index("LowTrust27Pct") < order.index("HighTrust")


def test_finish_difference_substitute_in_substitute_allowed_mode():
    req = source_request_from_dict(
        {
            "requested_quantity": 10,
            "today": "2026-03-01",
            "needed_by_date": "2026-03-10",
            "match_mode": "exact_preferred_substitutes_allowed",
        }
    )
    source = _base_source_profile() | {"finish": "zinc"}
    candidates = [
        {
            "vendor": "ExactFinish",
            "trust_tier": "High",
            "attributes": source,
            "pricing": {"item_total": 25.0, "shipping": 0.0, "fees": 0.0},
            "availability": {"estimated_arrival_date": "2026-03-05"},
        },
        {
            "vendor": "DifferentFinishCheaper",
            "trust_tier": "High",
            "attributes": _base_source_profile() | {"finish": "plain"},
            "pricing": {"item_total": 20.0, "shipping": 0.0, "fees": 0.0},
            "availability": {"estimated_arrival_date": "2026-03-05"},
        },
    ]

    ranked = evaluate_candidates(req, source, candidates)
    feasible = ranked.deadline_feasible_results
    by_vendor = {x.candidate.vendor: x for x in feasible}

    assert by_vendor["ExactFinish"].match_type == MatchType.EXACT_SPEC
    assert by_vendor["DifferentFinishCheaper"].match_type == MatchType.SUBSTITUTE
    # exact should outrank substitute despite higher price
    assert feasible[0].candidate.vendor == "ExactFinish"


def test_finish_difference_not_exact_in_exact_only_mode():
    req = source_request_from_dict(
        {
            "requested_quantity": 10,
            "today": "2026-03-01",
            "needed_by_date": "2026-03-10",
            "match_mode": "exact_only",
        }
    )
    source = _base_source_profile() | {"finish": "zinc"}
    candidate = {
        "vendor": "DifferentFinish",
        "trust_tier": "High",
        "attributes": _base_source_profile() | {"finish": "plain"},
        "pricing": {"item_total": 20.0, "shipping": 0.0, "fees": 0.0},
        "availability": {"estimated_arrival_date": "2026-03-05"},
    }

    ranked = evaluate_candidates(req, source, [candidate])
    result = ranked.deadline_feasible_results[0]
    assert result.match_type == MatchType.LOW_CONFIDENCE
    assert "finish" in result.missing_or_unverified_fields
