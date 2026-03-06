from __future__ import annotations

from abc import ABC, abstractmethod

from tool_finder.schemas import Candidate, FastenerProfile, SourceRequest


class BaseConnector(ABC):
    name: str
    connector_type: str

    @abstractmethod
    def search(self, source_request: SourceRequest, source_profile: FastenerProfile) -> list[Candidate]:
        raise NotImplementedError
