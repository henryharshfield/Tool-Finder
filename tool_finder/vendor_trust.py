from __future__ import annotations

from tool_finder.schemas import TrustTier


def normalize_trust_tier(raw: str | None, default: TrustTier = TrustTier.MEDIUM) -> TrustTier:
    if not raw:
        return default
    normalized = raw.strip().lower()
    mapping = {
        "high": TrustTier.HIGH,
        "medium": TrustTier.MEDIUM,
        "low": TrustTier.LOW,
    }
    return mapping.get(normalized, default)


def trust_rank(tier: TrustTier) -> int:
    ranks = {TrustTier.HIGH: 0, TrustTier.MEDIUM: 1, TrustTier.LOW: 2}
    return ranks[tier]


def low_trust_override_allowed(
    low_trust_unit_cost: float,
    high_trust_unit_cost: float,
    low_trust_uniquely_meets_deadline: bool = False,
) -> bool:
    if low_trust_uniquely_meets_deadline:
        return True
    # At least 25% cheaper.
    return low_trust_unit_cost <= high_trust_unit_cost * 0.75
