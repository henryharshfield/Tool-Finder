# TODO_BUILD_ORDER.md — Recommended Build Order

## Phase 1 — Schemas and rules
1. Build `schemas.py`
2. Build `ontology/fasteners.py`
3. Build `vendor_trust.py`

## Phase 2 — Core engines
4. Build `profile_builder.py`
5. Build `match_engine.py`
6. Build `deadline_engine.py`
7. Build `cost_engine.py`
8. Build `ranking_engine.py`
9. Build `explanations.py`

## Phase 3 — Connector framework
10. Build `supplier_connectors/base.py`
11. Build `supplier_connectors/registry.py`
12. Build `supplier_connectors/normalization.py`

## Phase 4 — First connectors
13. Build McMaster source connector
14. Build one API connector example
15. Build two scrape connector examples

## Phase 5 — Service layer
16. Build FastAPI endpoints
17. Add request validation
18. Add logging and error handling

## Phase 6 — Tests
19. Unit tests for ontology and match logic
20. Unit tests for cost + deadline engines
21. Fixture-driven tests for ranking
22. Connector normalization tests

## Definition of done for first usable backend
- accepts a source request
- builds a normalized fastener profile
- searches through configured connectors
- normalizes candidate results
- ranks candidates according to V1 rules
- returns grouped results with explanations
