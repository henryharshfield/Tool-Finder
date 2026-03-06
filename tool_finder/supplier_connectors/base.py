from __future__ import annotations

from typing import Literal, Protocol

from tool_finder.schemas import FastenerProfile, SourceRequest, SupplierCandidate, TrustTier


class SupplierConnector(Protocol):
    connector_name: str
    connector_type: Literal["api", "scrape", "discovery"]
    vendor_name: str | None
    trust_default: TrustTier | None

    def search(self, request: SourceRequest, profile: FastenerProfile) -> list[SupplierCandidate]:
        ...
