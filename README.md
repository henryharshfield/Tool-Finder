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
