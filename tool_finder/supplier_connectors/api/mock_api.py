from __future__ import annotations

from tool_finder.schemas import FastenerProfile, SourceRequest, SupplierCandidate, TrustTier


class MockApiConnector:
    connector_name = "mock_api"
    connector_type = "api"
    vendor_name = "MockAPI"
    trust_default = TrustTier.HIGH

    def __init__(self, candidates: list[SupplierCandidate] | None = None):
        self._candidates = candidates or []

    def search(self, request: SourceRequest, profile: FastenerProfile) -> list[SupplierCandidate]:
        return self._candidates
