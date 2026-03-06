from __future__ import annotations

from tool_finder.ontology.fasteners import is_supported_fastener_family, normalize_family
from tool_finder.schemas import FastenerProfile


def build_fastener_profile(source_profile: dict) -> FastenerProfile:
    family = normalize_family(source_profile["family"])
    if not is_supported_fastener_family(family):
        raise ValueError(f"Unsupported v1 family: {family}")

    return FastenerProfile(
        family=family,
        nominal_unit_system=source_profile["nominal_unit_system"].strip().lower(),
        diameter=source_profile.get("diameter"),
        thread_standard=source_profile.get("thread_standard"),
        thread_pitch_tpi=source_profile.get("thread_pitch_tpi"),
        thread_pitch_mm=source_profile.get("thread_pitch_mm"),
        length=source_profile.get("length"),
        head_type=source_profile.get("head_type"),
        material_family=source_profile.get("material_family"),
        finish=source_profile.get("finish"),
    )
