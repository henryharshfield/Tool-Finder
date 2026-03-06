from __future__ import annotations

from .schemas import TRUST_SCORES


def trust_score(tier: str) -> int:
    return TRUST_SCORES.get(tier, 2)


def low_trust_override_applies(
    low_trust_unit_cost: float,
    reference_higher_trust_unit_cost: float,
    uniquely_meets_deadline: bool,
) -> bool:
    if uniquely_meets_deadline:
        return True
    if reference_higher_trust_unit_cost <= 0:
        return False
    discount = 1 - (low_trust_unit_cost / reference_higher_trust_unit_cost)
    return discount >= 0.25
