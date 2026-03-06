from __future__ import annotations

from .ontology import normalize_family
from .schemas import FastenerProfile


def build_fastener_profile(raw_profile: dict) -> FastenerProfile:
    profile = dict(raw_profile)
    profile["family"] = normalize_family(profile["family"])
    return FastenerProfile(**profile)
