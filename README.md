# Prototype Part Sourcing Tool — Codex Starter Pack v2

`AGENTS.md` and `V1_RULES.md` are the primary implementation guardrails for Codex and should be treated as the source of truth for v1 behavior.

Use this starter pack together with:
- `prototype_part_sourcing_agent_design_brief.pdf`
- `codex_build_brief_part_sourcing_tool_v3.pdf`

## What changed in v2
This pack updates the project to use a **hybrid connector architecture**:
- API-first for structured, high-trust product/pricing/availability data
- Scraping/parsing connectors for important suppliers without practical public APIs
- Discovery connectors for broader market coverage later

## Core truth for v1
V1 remains:
- fasteners only
- backend first
- exact-match first
- substitutes only after exhaustive exact search
- no metric↔imperial equivalence for exact matching

## Important implementation guidance
Do **not** try to implement every supplier integration at once.

### Build the backend in two layers
1. **Connector framework**
   - a common interface for all supplier connectors
   - supports API connectors and scrape connectors
   - normalizes output into one candidate schema

2. **First practical V1 connectors**
   - McMaster source-profile connector
   - at least one API connector pattern
   - at least two scrape connector patterns relevant to fasteners

## Recommended V1 reality
For fasteners, broad market coverage will likely depend more on scraping/parsing connectors than on public supplier APIs.
Therefore:
- architect for many APIs,
- but do not block V1 on implementing all of them,
- and do not assume electronics-style API coverage exists for fasteners.

## New connector categories
- `supplier_connectors/api/`
- `supplier_connectors/scrape/`
- `supplier_connectors/discovery/`

## Priority for Codex
Prioritize:
- clean schemas
- ontology-driven matching
- deterministic ranking
- connector abstraction
- testability

Do not prioritize:
- fancy UI
- premature async orchestration
- implementing every connector before core ranking works

## Implemented backend scaffold (v1 milestone)

Current Python modules are under `tool_finder/`:
- `schemas.py`
- `ontology/fasteners.py`
- `vendor_trust.py`
- `profile_builder.py`
- `match_engine.py`
- `deadline_engine.py`
- `cost_engine.py`
- `ranking_engine.py`
- `explanations.py`
- `supplier_connectors/*`
- `service.py`
- `api.py` (FastAPI app with `/health` and `/evaluate`)

Test coverage is in `tests/test_v1_rules.py` and uses the fixture files in `fixtures/`.

## Run locally

### 1) Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e .
pip install pytest
```

### 2) Run tests
```bash
pytest -q
```

### 3) Start backend
```bash
uvicorn tool_finder.api:app --host 0.0.0.0 --port 8000 --reload
```

### 4) Send example request
```bash
cat > /tmp/example_request.json <<'JSON'
{
  "source_request": {
    "requested_quantity": 10,
    "today": "2026-03-01",
    "needed_by_date": "2026-03-11",
    "match_mode": "exact_preferred_substitutes_allowed",
    "country_filter": null,
    "shipping_destination": "US-TX"
  },
  "source_profile": {
    "fastener_family": "bolt",
    "nominal_unit_system": "imperial",
    "diameter": "1/4 in",
    "thread_standard": "UNC",
    "thread_pitch_tpi": 20,
    "length": "1-1/2 in",
    "head_type": "hex",
    "material_family": "18-8 stainless steel",
    "finish": "plain"
  },
  "candidates": [
    {
      "vendor": "HighTrust A",
      "trust_tier": "High",
      "source_tier": "preferred",
      "listing_url": "https://example.com/a",
      "attributes": {
        "fastener_family": "bolt",
        "nominal_unit_system": "imperial",
        "diameter": "1/4 in",
        "thread_standard": "UNC",
        "thread_pitch_tpi": 20,
        "length": "1-1/2 in",
        "head_type": "hex",
        "material_family": "18-8 stainless steel",
        "finish": "plain"
      },
      "pricing": {
        "item_total": 21.0,
        "shipping": 6.5,
        "fees": 0.0,
        "tariff_status": "unknown"
      },
      "availability": {
        "estimated_arrival_date": "2026-03-08",
        "stock_status": "in_stock"
      },
      "moq": 10,
      "country_of_origin": "Germany"
    },
    {
      "vendor": "HighTrust B",
      "trust_tier": "High",
      "source_tier": "broader",
      "listing_url": "https://example.com/b",
      "attributes": {
        "fastener_family": "bolt",
        "nominal_unit_system": "imperial",
        "diameter": "1/4 in",
        "thread_standard": "UNC",
        "thread_pitch_tpi": 20,
        "length": "1-1/2 in",
        "head_type": "hex",
        "material_family": "18-8 stainless steel",
        "finish": "plain"
      },
      "pricing": {
        "item_total": 18.0,
        "shipping": 12.0,
        "fees": 0.0,
        "tariff_status": "unknown"
      },
      "availability": {
        "estimated_arrival_date": "2026-03-06",
        "stock_status": "in_stock"
      },
      "moq": 10,
      "country_of_origin": "Germany"
    }
  ]
}
JSON

curl -sS -X POST "http://127.0.0.1:8000/evaluate" \
  -H "Content-Type: application/json" \
  --data-binary @/tmp/example_request.json > /tmp/example_response.json
```

### 5) Inspect response
```bash
python -m json.tool /tmp/example_response.json | sed -n '1,120p'
```

Optional with `jq`:
```bash
jq '.deadline_feasible_results[] | {vendor, match_type, effective_unit_cost, deadline_status}' /tmp/example_response.json
```
