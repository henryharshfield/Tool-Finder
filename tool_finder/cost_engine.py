from __future__ import annotations

from tool_finder.schemas import Pricing, SourceRequest, SupplierCandidate


def delivered_total(pricing: Pricing) -> float:
    return pricing.item_total + pricing.shipping + pricing.fees


def effective_unit_cost(candidate: SupplierCandidate, request: SourceRequest) -> float | None:
    if candidate.pricing is None:
        return None
    total = delivered_total(candidate.pricing)
    # V1 MOQ rule: divide by requested quantity even if below MOQ.
    return total / request.requested_quantity
