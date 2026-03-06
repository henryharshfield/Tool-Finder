from __future__ import annotations

from tool_finder.schemas import FastenerProfile, SourceRequest, SupplierCandidate, TrustTier


class MockScrapeConnectorA:
    connector_name = "mock_scrape_a"
    connector_type = "scrape"
    vendor_name = "MockScrapeA"
    trust_default = TrustTier.MEDIUM

    def __init__(self, candidates: list[SupplierCandidate] | None = None):
        self._candidates = candidates or []

    def search(self, request: SourceRequest, profile: FastenerProfile) -> list[SupplierCandidate]:
        return self._candidates
