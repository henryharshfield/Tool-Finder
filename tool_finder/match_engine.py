from __future__ import annotations

from .schemas import FastenerProfile, MatchMode, MatchType

DISQUALIFYING_FIELDS = (
    "family",
    "diameter",
    "thread_standard",
    "length",
    "head_type",
    "material_family",
)

SUBSTITUTE_ONLY_FIELDS = ("finish",)


def _pitch_value(attrs: dict) -> tuple[str, str | int | float | None]:
    if attrs.get("thread_pitch_tpi") is not None:
        return ("thread_pitch_tpi", attrs.get("thread_pitch_tpi"))
    return ("thread_pitch_mm", attrs.get("thread_pitch_mm"))


def classify_match(
    source: FastenerProfile,
    candidate_attributes: dict,
    match_mode: MatchMode,
) -> tuple[MatchType, list[str], list[str]]:
    matched_fields: list[str] = []
    missing_or_unverified: list[str] = []

    if candidate_attributes.get("nominal_unit_system") != source.nominal_unit_system:
        return MatchType.LOW_CONFIDENCE, matched_fields, ["metric_imperial_system_mismatch"]

    candidate_pitch_name, candidate_pitch = _pitch_value(candidate_attributes)
    source_pitch_name, source_pitch = _pitch_value(source.__dict__)
    if source_pitch_name != candidate_pitch_name or source_pitch != candidate_pitch:
        return MatchType.LOW_CONFIDENCE, matched_fields, ["thread_pitch_mismatch"]

    disqualifying_mismatch = False
    substitute_diffs = 0
    for field in DISQUALIFYING_FIELDS:
        source_value = getattr(source, field)
        candidate_value = candidate_attributes.get(field)
        if candidate_value is None:
            missing_or_unverified.append(field)
            disqualifying_mismatch = True
        elif candidate_value == source_value:
            matched_fields.append(field)
        else:
            missing_or_unverified.append(f"{field}_mismatch")
            disqualifying_mismatch = True

    for field in SUBSTITUTE_ONLY_FIELDS:
        source_value = getattr(source, field)
        candidate_value = candidate_attributes.get(field)
        if source_value is None or candidate_value is None:
            continue
        if source_value != candidate_value:
            substitute_diffs += 1
            missing_or_unverified.append(f"{field}_diff")
        else:
            matched_fields.append(field)

    if not disqualifying_mismatch and substitute_diffs == 0:
        if source.mpn and candidate_attributes.get("mpn") == source.mpn:
            return MatchType.EXACT_OEM, matched_fields, missing_or_unverified
        return MatchType.EXACT_SPEC, matched_fields, missing_or_unverified

    if not disqualifying_mismatch and match_mode == MatchMode.EXACT_PREFERRED_SUBSTITUTES_ALLOWED:
        return MatchType.SUBSTITUTE, matched_fields, missing_or_unverified

    return MatchType.LOW_CONFIDENCE, matched_fields, missing_or_unverified
