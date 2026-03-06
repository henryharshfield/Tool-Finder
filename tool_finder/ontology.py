from __future__ import annotations

SUPPORTED_FAMILIES = {"bolt", "screw", "nut", "washer", "threaded rod", "set screw"}


def normalize_family(value: str) -> str:
    normalized = value.strip().lower()
    aliases = {
        "bolts": "bolt",
        "screws": "screw",
        "nuts": "nut",
        "washers": "washer",
        "threaded_rod": "threaded rod",
        "set_screws": "set screw",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in SUPPORTED_FAMILIES:
        raise ValueError(f"Unsupported fastener family for v1: {value}")
    return normalized
