# TEST_CASES.md

## Purpose
These are behavioral expectations for the first backend.

## Test Case 1 — exact spec, cheaper, meets deadline
Expect:
- ranked high
- `match_type = exact_spec`
- appears in `deadline_feasible_results`

## Test Case 2 — exact spec, cheaper, misses deadline slightly
Expect:
- appears in `missed_deadline_results`
- classified as `slight_miss`

## Test Case 3 — low trust but 25% cheaper
Expect:
- may rise, but only if override rule is satisfied

## Test Case 4 — metric candidate for imperial source
Expect:
- not exact equivalent in v1

## Test Case 5 — substitute with different finish only
Expect:
- appears only after exact search exhausted and only if substitute mode allows it
