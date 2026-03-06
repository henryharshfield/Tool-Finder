from __future__ import annotations

from dataclasses import dataclass, field

from tool_finder.schemas import FastenerProfile, SourceRequest, SupplierCandidate
from tool_finder.supplier_connectors.base import SupplierConnector


@dataclass
class ConnectorRegistry:
    connectors: list[SupplierConnector] = field(default_factory=list)

    def register(self, connector: SupplierConnector) -> None:
        self.connectors.append(connector)

    def search_all(self, request: SourceRequest, profile: FastenerProfile) -> list[SupplierCandidate]:
        results: list[SupplierCandidate] = []
        for connector in self.connectors:
            results.extend(connector.search(request, profile))
        return results
