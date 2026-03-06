# AGENTS.md

## Project purpose

This repository is for building the **v1 backend** of a prototype-part sourcing tool.

The product’s purpose is to help engineers find **cheaper, trustworthy alternatives** to source listings from suppliers such as McMaster-Carr or Mouser while preserving match quality and practical usability.

V1 is intentionally narrow:
- backend only
- fasteners only
- exact-match-first
- hybrid connector architecture (API + scraping)
- no frontend/UI work unless explicitly requested later

---

## Source-of-truth files

Read these files before making changes:

1. `V1_RULES.md` — primary behavioral spec
2. `README.md` — project overview
3. `CONNECTORS.md` — connector architecture and strategy
4. `TODO_BUILD_ORDER.md` — preferred implementation order
5. `TEST_CASES.md` — expected behaviors
6. `fixtures/fastener_fixture_1.json`
7. `fixtures/fastener_fixture_2.json`
8. `fixtures/fastener_fixture_3.json`
9. `fixtures/fastener_fixture_4.json`
10. `fixtures/fastener_fixture_5.json`
11. `docs/prototype_part_sourcing_agent_design_brief.pdf`
12. `docs/codex_build_brief_part_sourcing_tool_v3.pdf`

### Conflict resolution
If files appear to conflict:
- `V1_RULES.md` wins for behavioral logic
- `CONNECTORS.md` wins for connector strategy
- `TODO_BUILD_ORDER.md` wins for build order
- the PDFs provide architecture and product context, but markdown files are the working implementation spec

Do not invent new product behavior if the existing files already define it.

---

## Non-negotiable v1 boundaries

### Scope
V1 is **fasteners only**.

Supported families in v1:
- bolts
- screws
- nuts
- washers
- threaded rod
- set screws

Do not expand into bearings, connectors, electronics, pins, clips, rivets, anchors, or other categories unless explicitly asked.

### Backend only
Build the backend first.
Do **not** build:
- frontend
- UI
- dashboards
- browser app
- authentication
- production deployment setup

unless explicitly requested later.

### Exact matching rules
V1 must preserve the exact/substitute ordering:

1. Exact OEM
2. Exact Spec
3. Substitute
4. Low Confidence

Substitutes must only appear after exhaustive exact-match search, and only if substitute mode allows them.

### No metric/imperial equivalence for exact matching
Do **not** treat metric and imperial fasteners as exact equivalents in v1.

If the source and candidate are in different nominal systems:
- do not convert them to force equivalence
- do not classify them as exact-spec matches

This is a hard v1 rule.

### Ranking priorities
For deadline-feasible results, ranking should primarily optimize for:
1. match class
2. delivered per-unit cost at requested quantity
3. vendor trust
4. arrival timing only as a minor tie-break

Do not reward “earlier than needed” in a major way once the deadline is already met.

### Deadline grouping
Results must be separated into:
- `deadline_feasible_results`
- `missed_deadline_results`

Use the 125% slight-miss rule defined in `V1_RULES.md`.

### Trust override rule
Low-trust vendors should rank below higher-trust vendors unless they are:
- at least 25% cheaper after delivered-cost math, or
- uniquely able to meet the deadline

### MOQ rule
If requested quantity is lower than MOQ, compute effective per-unit cost using the **requested quantity**, not the MOQ.

### Country of origin
Country of origin matters only when the user explicitly requests it.
Otherwise treat it as informational only.

---

## Architecture expectations

Build the backend as a **modular Python codebase** with clear separation of concerns.

Preferred structure:
- schemas
- ontology
- profile builder
- match engine
- deadline engine
- cost engine
- ranking engine
- vendor trust module
- explanations
- connector framework
- tests

### Hybrid connector architecture
The backend must support:
- API connectors
- scrape connectors
- discovery connectors later

Do not assume APIs alone cover the entire market.
Do not assume scraping is always available.
Design connectors behind a common interface so connectors can be added, removed, or repaired without changing ranking logic.

### Connector separation
Do not mix:
- parsing logic
- ranking logic
- trust logic
- cost logic

Connector-specific extraction should stay inside connector modules.
Normalized candidate objects should be passed into the core engines.

---

## Coding expectations

### General expectations
Write code that is:
- modular
- explicit
- testable
- readable
- conservative rather than clever

Prefer transparent rules over hidden heuristics.

### Avoid overengineering
For v1:
- keep abstractions practical
- do not build a giant generalized ontology system
- do not build unnecessary infrastructure
- do not optimize for scale before correctness

### Prefer deterministic logic
Important business rules must live in code, not only in prompts or comments.

This especially applies to:
- exact vs substitute classification
- vendor trust scoring
- cost calculations
- deadline classification
- ranking behavior

### Be cautious with assumptions
If a rule is not defined, choose the simplest behavior that preserves existing specs and does not expand scope.

Do not silently broaden product scope.

---

## Testing expectations

The fixture JSON files are not decorative. They should be used as:
- schema examples
- test fixtures
- ranking behavior checks
- matching behavior checks

At minimum, create tests for:
- ontology classification behavior
- exact vs substitute matching
- metric/imperial non-equivalence
- MOQ cost behavior
- 125% slight-miss deadline logic
- vendor trust override behavior
- grouping into feasible vs missed-deadline results

Prefer unit tests first.
Add integration-style tests only after core engines are stable.

---

## Recommended implementation order

Follow `TODO_BUILD_ORDER.md`.

High-level order:
1. schemas
2. fastener ontology
3. vendor trust rules
4. profile builder
5. match engine
6. deadline engine
7. cost engine
8. ranking engine
9. explanations
10. connector framework
11. initial connectors
12. service layer / API endpoints
13. tests and refinement

Do not start with UI or broad connector expansion.

---

## First milestone

The first milestone should produce a backend that can:
- accept a normalized source request
- build a normalized fastener profile
- run through configured connectors
- normalize supplier candidates
- classify match type
- compute delivered cost
- classify deadline status
- score vendor trust
- rank candidates
- return grouped results with structured explanations
- run tests against the provided fixture files

A partial but clean backend scaffold is better than broad, messy implementation.

---

## Output expectations for ranked results

Each ranked result should be able to support output fields such as:
- match type
- confidence
- delivered cost
- availability / arrival estimate
- vendor trust
- country of origin if known
- matched fields
- unverified or missing fields
- explanation of why it ranked where it did

Keep output structures clean and machine-readable.

---

## What not to do

Do not:
- add UI
- expand beyond fasteners
- implement metric/imperial forced equivalence
- intertwine connector parsing with ranking logic
- hide business rules inside vague heuristics
- ignore the fixture files
- skip tests for core engines
- make a marketplace-scraper-first architecture
- assume every supplier has a usable API
- assume every supplier is scrape-friendly

---

## Working style

Before major implementation work:
1. read the source-of-truth files
2. summarize the implementation plan
3. propose file/module structure
4. then implement

When uncertain, stay within the explicit v1 rules and keep the design simple.

Prioritize correctness, transparency, and clean structure over speed.
Take the time needed to build a clean first backend.
