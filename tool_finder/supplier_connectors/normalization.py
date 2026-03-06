from __future__ import annotations

from datetime import date

from tool_finder.schemas import Availability, Pricing, SupplierCandidate
from tool_finder.vendor_trust import normalize_trust_tier


def normalize_candidate(raw: dict) -> SupplierCandidate:
    arrival = None
    availability = raw.get("availability") or {}
    if availability.get("estimated_arrival_date"):
        arrival = date.fromisoformat(availability["estimated_arrival_date"])

    pricing = None
    if raw.get("pricing"):
        p = raw["pricing"]
        pricing = Pricing(
            item_total=float(p.get("item_total", 0.0)),
            shipping=float(p.get("shipping", 0.0)),
            fees=float(p.get("fees", 0.0)),
            tariff_status=p.get("tariff_status"),
        )

    return SupplierCandidate(
        vendor=raw["vendor"],
        trust_tier=normalize_trust_tier(raw.get("trust_tier")),
        source_tier=raw.get("source_tier"),
        listing_url=raw.get("listing_url"),
        attributes=raw.get("attributes", {}),
        pricing=pricing,
        availability=Availability(estimated_arrival_date=arrival, stock_status=availability.get("stock_status")),
        moq=int(raw.get("moq", 1)),
        country_of_origin=raw.get("country_of_origin"),
    )
