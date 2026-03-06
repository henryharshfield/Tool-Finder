from __future__ import annotations

from tool_finder.schemas import FastenerProfile, MatchMode, MatchType, SupplierCandidate

REQUIRED_EXACT_FIELDS = [
    "family",
    "nominal_unit_system",
    "diameter",
    "thread_standard",
    "length",
    "material_family",
]



def classify_match(
    source: FastenerProfile,
    candidate: SupplierCandidate,
    match_mode: MatchMode,
) -> tuple[MatchType, float, list[str], list[str]]:
    attrs = candidate.attributes

    # Hard v1 rule: never exact across unit systems.
    if attrs.get("nominal_unit_system", "").strip().lower() != source.nominal_unit_system:
        return MatchType.LOW_CONFIDENCE, 0.2, [], ["nominal_unit_system"]

    matched: list[str] = []
    missing: list[str] = []

    def check(field: str, source_value):
        if source_value is None:
            return
        cand_val = attrs.get(field)
        if cand_val == source_value:
            matched.append(field)
        else:
            missing.append(field)

    check("family", source.family)
    check("diameter", source.diameter)
    check("thread_standard", source.thread_standard)
    check("length", source.length)
    check("material_family", source.material_family)

    # Thread pitch: compare whichever system source uses.
    if source.thread_pitch_tpi is not None:
        check("thread_pitch_tpi", source.thread_pitch_tpi)
    if source.thread_pitch_mm is not None:
        check("thread_pitch_mm", source.thread_pitch_mm)

    if not missing:
        if attrs.get("manufacturer_part_number") and attrs.get("manufacturer_part_number") == attrs.get("source_manufacturer_part_number"):
            return MatchType.EXACT_OEM, 1.0, matched, []
        return MatchType.EXACT_SPEC, 0.95, matched, []

    # Candidate can still be substitute for non-critical differences only.
    critical = {"family", "diameter", "thread_standard", "thread_pitch_tpi", "thread_pitch_mm", "length", "material_family"}
    critical_misses = [m for m in missing if m in critical]
    if critical_misses:
        return MatchType.LOW_CONFIDENCE, 0.3, matched, missing

    if match_mode == MatchMode.EXACT_ONLY:
        return MatchType.LOW_CONFIDENCE, 0.3, matched, missing

    return MatchType.SUBSTITUTE, 0.65, matched, missing
