from __future__ import annotations

FASTENER_FAMILIES = {
    "bolt",
    "screw",
    "nut",
    "washer",
    "threaded rod",
    "set screw",
}


def normalize_family(value: str) -> str:
    normalized = value.strip().lower()
    aliases = {
        "bolts": "bolt",
        "screws": "screw",
        "nuts": "nut",
        "washers": "washer",
        "threaded_rod": "threaded rod",
        "set_screw": "set screw",
    }
    return aliases.get(normalized, normalized)


def is_supported_fastener_family(value: str) -> bool:
    return normalize_family(value) in FASTENER_FAMILIES
