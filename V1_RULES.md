# V1 Rules — Fasteners Only

## Scope
V1 applies only to fasteners:
- bolts
- screws
- nuts
- washers
- threaded rod
- set screws

Do not add other part families in v1.

## Matching order
1. Exact OEM
2. Exact Spec
3. Substitute
4. Low Confidence

## Visible user toggle
- `exact_only`
- `exact_preferred_substitutes_allowed`

Substitutes must rank lower and appear only after exhaustive exact-match search.

## Unit-system rule
Do not convert imperial fasteners to metric or metric fasteners to imperial for equivalence in v1.
If source and candidate are in different nominal systems, treat them as non-identical for exact equivalence.

## Required fields for exact-spec fastener match
- fastener family
- nominal unit system and designation
- diameter
- thread standard
- thread pitch or TPI
- length when applicable
- head type or drive style when applicable
- material family

## Preferred fields
- finish or coating
- strength grade or property class
- head dimensions
- thread direction
- point style
- relevant standard designation
- manufacturer part number if known

## Optional or informational fields
- country of origin unless explicitly requested
- packaging style
- heat treat if source omits it
- seller marketing descriptors

## Disqualifying mismatches for exact-spec
- different fastener family
- different diameter
- different thread pitch or TPI
- different thread standard when functionally incompatible
- different nominal length
- different head type when fit/use changes
- different material family
- metric vs imperial nominal system mismatch

## Allowed substitute-only differences
- different finish or coating
- equivalent or better strength grade when fit and function are preserved
- country of origin when not requested
- minor packaging differences

## Deadline classification
Let:
- `today`
- `needed_by_date`
- `candidate_arrival_date`
- `time_window = needed_by_date - today`
- `slight_miss_cutoff = today + 1.25 * time_window`

Classify as:
- `deadline_feasible` if `candidate_arrival_date <= needed_by_date`
- `slight_miss` if `needed_by_date < candidate_arrival_date <= slight_miss_cutoff`
- `future_option_only` if `candidate_arrival_date > slight_miss_cutoff`

## Ranking behavior
### Top-level grouping
- Group 1: deadline-feasible results
- Group 2: missed-deadline results

### Main ranking inside deadline-feasible results
Order primarily by:
1. match class
2. delivered per-unit cost at requested quantity
3. vendor trust
4. arrival timing only as a minor tie-break

### Missed-deadline results
- `slight_miss` above `future_option_only`
- very attractive slow options may be surfaced as future-use options

## Vendor trust override rule
Low-trust vendors rank below higher-trust vendors unless they are:
- at least 25% cheaper after delivered-cost math, or
- uniquely able to meet the deadline

## Country of origin behavior
Country of origin matters only when explicitly requested.
If requested, non-matching countries are filtered out.
Otherwise treat country of origin as informational only.

## Cost rules
Optimize for delivered per-unit cost to the door at the requested quantity.

### Delivered cost components
- item price
- shipping estimate if shipping is unknown
- explicit fees if implied on the page and estimable
- tariffs should not be estimated if unknown; mark as unknown instead

### MOQ rule
If requested quantity is lower than MOQ, compute effective per-unit cost using the requested quantity, not the MOQ.
