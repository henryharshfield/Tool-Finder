from __future__ import annotations

from tool_finder.connectors.base import BaseConnector
from tool_finder.schemas import Candidate, FastenerProfile, SourceRequest


class ConnectorRegistry:
    def __init__(self) -> None:
        self._connectors: dict[str, BaseConnector] = {}

    def register(self, connector: BaseConnector) -> None:
        self._connectors[connector.name] = connector

    def available_connectors(self) -> list[str]:
        return sorted(self._connectors.keys())

    def run_all(self, source_request: SourceRequest, source_profile: FastenerProfile) -> list[Candidate]:
        all_candidates: list[Candidate] = []
        for connector in self._connectors.values():
            all_candidates.extend(connector.search(source_request, source_profile))
        return all_candidates
