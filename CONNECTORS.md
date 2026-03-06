# CONNECTORS.md — Hybrid Connector Strategy

## Core design decision
The backend must support **hybrid search**:
1. API connectors for structured data
2. Scrape connectors for mechanical coverage gaps
3. Discovery connectors for later market expansion

The system should not assume APIs alone are enough for all mechanical and electrical prototyping.

## Connector interface contract
Every connector should implement a normalized interface:

```python
class SupplierConnector(Protocol):
    connector_name: str
    connector_type: Literal["api", "scrape", "discovery"]
    vendor_name: str | None
    trust_default: Literal["high", "medium", "low"] | None

    def search(self, request: SourceRequest, profile: FastenerProfile) -> list[SupplierCandidate]:
        ...
```

Each connector returns normalized `SupplierCandidate` objects.

## Candidate fields each connector should try to provide
- vendor_name
- vendor_url
- product_url
- sku_or_part_number
- manufacturer_name
- manufacturer_part_number
- title
- extracted_attributes
- available_quantity
- MOQ
- unit_price
- price_breaks
- stock_status
- lead_time_days or estimated_arrival
- shipping_cost if known
- fee_estimates if known
- country_of_origin if known
- datasheet_url if known
- source_confidence
- raw_source_payload

## Top 10 APIs to architect for
These APIs should be represented in configuration and connector planning even if not all are implemented in milestone 1.

1. Nexar / Octopart
2. DigiKey
3. Mouser
4. Arrow
5. Avnet
6. element14 / Newark / Farnell
7. TME
8. LCSC
9. McMaster-Carr
10. Master Electronics

## Important V1 reality
V1 is fasteners-only.
That means broad coverage will likely require scrape connectors for sites that matter in mechanical sourcing.
Therefore the connector framework must support scraping from the beginning.

## Recommended first implementation order
### Milestone 1: connector framework only
- base connector interface
- connector registry
- normalization helpers
- retry + logging helpers

### Milestone 2: source profiling
- McMaster source-profile connector
- source-page extraction fallback if API unavailable

### Milestone 3: first candidate connectors
Implement a small set that proves both patterns:
- 1 API connector pattern
- 2 scrape connector patterns

### Milestone 4: trust + ranking integration
Ensure connector outputs flow through:
- match engine
- cost engine
- deadline engine
- ranking engine

## Vendor trust strategy
Do not hardcode a giant vendor list as the primary logic.
Instead:
- maintain a small optional manual override table
- otherwise compute trust from explicit signals

### Signals that raise trust
- manufacturer-direct or authorized distributor
- clear product identity and business identity
- structured specs
- explicit stock / lead-time info
- clear return/warranty policy
- established distributor characteristics

### Signals that lower trust
- marketplace ambiguity
- sparse specs
- no clear stock/lead-time info
- unclear seller identity
- weak authenticity signals

## What Codex should not do
- do not intertwine connector-specific parsing with ranking logic
- do not make the ranking engine vendor-specific
- do not depend on every API being available at first
- do not assume electronics APIs cover mechanical fasteners well
