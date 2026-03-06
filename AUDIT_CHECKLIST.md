# V1 Backend Audit Checklist

Audit target: latest implementation in `tool_finder/` validated against `AGENTS.md`, `V1_RULES.md`, `CONNECTORS.md`, `TODO_BUILD_ORDER.md`, and `TEST_CASES.md`.

Status legend:
- **Fully implemented**
- **Partially implemented**
- **Missing**

| Requirement | Where implemented | Status | Deviations / notes |
|---|---|---|---|
| V1 scope is fasteners-only families (bolt/screw/nut/washer/threaded rod/set screw) | `tool_finder/ontology/fasteners.py` (`FASTENER_FAMILIES` + normalization), `tool_finder/profile_builder.py` family check | **Fully implemented** | Rejects unsupported families with `ValueError`. |
| Backend-only (no frontend/UI) | Repository structure | **Fully implemented** | No frontend files added. |
| Match ordering supports Exact OEM → Exact Spec → Substitute → Low Confidence | `tool_finder/schemas.py` (`MatchType` enum), `tool_finder/ranking_engine.py` (`_MATCH_RANK`) | **Fully implemented** | Ordering exists in ranking keys. |
| Substitutes appear only when allowed by mode (`exact_only` vs substitutes allowed) | `tool_finder/match_engine.py` (`match_mode == EXACT_ONLY` handling) | **Partially implemented** | Enforces mode at candidate classification level, but does **not** enforce “exhaustive exact search first” as a two-phase search pipeline. |
| Metric/imperial non-equivalence for exact matching | `tool_finder/match_engine.py` early unit-system mismatch check | **Fully implemented** | Mismatch returns `LOW_CONFIDENCE`; never exact. |
| Exact-spec required fields include family/unit system/diameter/thread standard/pitch/length/material | `tool_finder/match_engine.py` required checks | **Partially implemented** | Head type/drive applicability from `V1_RULES.md` not enforced in exact-spec logic. |
| Disqualifying mismatches for exact-spec | `tool_finder/match_engine.py` `critical` set | **Partially implemented** | Critical mismatches handled, but thread compatibility nuance and head-type mismatch disqualifier are incomplete. |
| Allowed substitute-only differences (finish, grade, etc.) | `tool_finder/match_engine.py` non-critical fallback -> `SUBSTITUTE` | **Partially implemented** | No explicit rule encoding for strength-grade equivalence / specific allowed deltas. |
| Deadline classification: feasible / slight_miss / future_option_only with 125% rule | `tool_finder/deadline_engine.py` | **Fully implemented** | Uses `today + 1.25 * time_window`. |
| Group results into `deadline_feasible_results` and `missed_deadline_results` | `tool_finder/ranking_engine.py` and `tool_finder/schemas.py` (`RankedResults`) | **Partially implemented** | Items with unknown deadline (`deadline_status=None`) are treated as feasible; spec is silent, but this is a policy assumption. |
| Rank feasible results by match class, delivered unit cost, trust, and only minor arrival tie-break | `tool_finder/ranking_engine.py` `_base_sort_key` | **Fully implemented** | Arrival is last key (minor tie-break). |
| Trust override: low-trust ranks below unless >=25% cheaper or uniquely meets deadline | `tool_finder/vendor_trust.py`, `tool_finder/ranking_engine.py` | **Partially implemented** | 25% cheaper implemented; “uniquely meets deadline” flag exists in helper but is not computed/used by ranking flow. |
| MOQ rule: effective unit cost uses requested quantity even if request < MOQ | `tool_finder/cost_engine.py` | **Fully implemented** | Ignores MOQ denominator and divides by requested quantity. |
| Country-of-origin only filters when explicitly requested | `tool_finder/service.py` | **Partially implemented** | Filtering only applies when candidate country is known; unknown-country candidates still pass when filter is set. |
| Delivered cost includes item + shipping + fees; tariffs unknown handled explicitly | `tool_finder/cost_engine.py`, `tool_finder/schemas.py` | **Partially implemented** | Cost components supported, but no dedicated “tariff unknown” explanation/flag propagation in ranking output. |
| Connector framework supports API/scrape/discovery via common interface | `tool_finder/supplier_connectors/base.py`, mock connectors under `api/`, `scrape/`, discovery placeholder | **Partially implemented** | Interface exists and mock patterns exist; no retry/logging helpers from connector milestone guidance. |
| Connector normalization separated from core ranking/matching | `tool_finder/supplier_connectors/normalization.py` and `tool_finder/service.py` | **Fully implemented** | Candidate parsing happens in normalization before engine evaluation. |
| First practical connectors: McMaster source connector + 1 API + 2 scrape patterns | `tool_finder/supplier_connectors/api/mock_api.py`, `scrape/mock_scrape_a.py`, `scrape/mock_scrape_b.py` | **Partially implemented** | API + 2 scrape patterns exist as mocks; McMaster source-profile connector is missing. |
| Service layer / API endpoints | none | **Missing** | No FastAPI endpoints, request validation layer, or service API module. |
| Output includes ranked explanation + matched and missing fields | `tool_finder/schemas.py`, `tool_finder/explanations.py`, `tool_finder/service.py` | **Partially implemented** | Fields are present; explanations are currently very short and not deeply structured. |
| Tests: ontology classification | `tests/test_v1_rules.py::test_ontology_supported_family` | **Fully implemented** | Covered. |
| Tests: exact vs substitute matching | `tests/test_v1_rules.py` | **Partially implemented** | No direct assertion that substitute appears only after exact search exhausted; tests mostly assert non-exact for metric mismatch. |
| Tests: metric/imperial non-equivalence | `tests/test_v1_rules.py::test_metric_imperial_non_equivalence_fixture_2` | **Fully implemented** | Covered. |
| Tests: MOQ behavior | `tests/test_v1_rules.py::test_moq_requested_quantity_cost_fixture_5` | **Fully implemented** | Covered. |
| Tests: 125% slight-miss logic | `tests/test_v1_rules.py::test_deadline_125_percent_rule_fixture_3` | **Fully implemented** | Covered. |
| Tests: vendor trust override behavior | `tests/test_v1_rules.py::test_trust_override_threshold_fixture_4` | **Partially implemented** | Tests helper threshold only; does not test full ranking branch for unique-deadline override. |
| Tests: grouping feasible vs missed-deadline | `tests/test_v1_rules.py::test_deadline_125_percent_rule_fixture_3` | **Fully implemented** | Grouping behavior implicitly validated via combined statuses. |

## High-priority gaps to fix next

1. Implement explicit two-phase search behavior to guarantee substitutes are only considered after exact search is exhausted.
2. Complete exact-spec disqualifier logic for head type / functional compatibility nuances from `V1_RULES.md`.
3. Implement unique-deadline trust override in `ranking_engine` rather than only helper-level support.
4. Add real service endpoints (FastAPI) and request validation per `TODO_BUILD_ORDER.md` phase 5.
5. Add a McMaster source-profile connector (non-mock) and connector retry/logging helpers.
6. Tighten country filter semantics for unknown country values when user explicitly requests country matching.
