from __future__ import annotations

from tool_finder.schemas import FastenerProfile, MatchMode, MatchType, SupplierCandidate

REQUIRED_EXACT_FIELDS = [
    "fastener_family",
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

    # Hard v1 rule: metric/imperial cross-system can never be exact in v1.
    candidate_system = attrs.get("nominal_unit_system", "").strip().lower()
    if candidate_system != source.nominal_unit_system:
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

    check("fastener_family", source.fastener_family)
    check("diameter", source.diameter)
    check("thread_standard", source.thread_standard)
    check("length", source.length)
    check("material_family", source.material_family)

    if source.thread_pitch_tpi is not None:
        check("thread_pitch_tpi", source.thread_pitch_tpi)
    if source.thread_pitch_mm is not None:
        check("thread_pitch_mm", source.thread_pitch_mm)

    # Finish/coating difference is substitute-level when source specifies finish.
    if source.finish is not None:
        check("finish", source.finish)

    if not missing:
        if attrs.get("manufacturer_part_number") and attrs.get("manufacturer_part_number") == attrs.get("source_manufacturer_part_number"):
            return MatchType.EXACT_OEM, 1.0, matched, []
        return MatchType.EXACT_SPEC, 0.95, matched, []

    critical = {
        "fastener_family",
        "diameter",
        "thread_standard",
        "thread_pitch_tpi",
        "thread_pitch_mm",
        "length",
        "material_family",
    }
    critical_misses = [m for m in missing if m in critical]
    if critical_misses:
        return MatchType.LOW_CONFIDENCE, 0.3, matched, missing

    if match_mode == MatchMode.EXACT_ONLY:
        return MatchType.LOW_CONFIDENCE, 0.3, matched, missing

    return MatchType.SUBSTITUTE, 0.65, matched, missing
