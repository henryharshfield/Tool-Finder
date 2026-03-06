from __future__ import annotations

from .schemas import Candidate


def compute_delivered_total(candidate: Candidate) -> float:
    if candidate.pricing is None:
        return 0.0
    if candidate.pricing.delivered_total is not None:
        return float(candidate.pricing.delivered_total)
    item = candidate.pricing.item_total or 0.0
    shipping = candidate.pricing.shipping or 0.0
    fees = candidate.pricing.fees or 0.0
    return float(item + shipping + fees)


def compute_effective_unit_cost(candidate: Candidate, requested_quantity: int) -> float:
    delivered_total = compute_delivered_total(candidate)
    denominator = max(requested_quantity, 1)
    return delivered_total / denominator
