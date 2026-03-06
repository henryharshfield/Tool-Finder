from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any


class MatchMode(str, Enum):
    EXACT_ONLY = "exact_only"
    EXACT_PREFERRED_SUBSTITUTES_ALLOWED = "exact_preferred_substitutes_allowed"


class MatchType(str, Enum):
    EXACT_OEM = "exact_oem"
    EXACT_SPEC = "exact_spec"
    SUBSTITUTE = "substitute"
    LOW_CONFIDENCE = "low_confidence"


class DeadlineStatus(str, Enum):
    DEADLINE_FEASIBLE = "deadline_feasible"
    SLIGHT_MISS = "slight_miss"
    FUTURE_OPTION_ONLY = "future_option_only"


class TrustTier(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(slots=True)
class SourceRequest:
    requested_quantity: int
    needed_by_date: date | None = None
    today: date | None = None
    country_filter: str | None = None
    shipping_destination: str | None = None
    match_mode: MatchMode = MatchMode.EXACT_PREFERRED_SUBSTITUTES_ALLOWED
    input_type: str | None = None
    raw_input: str | None = None


@dataclass(slots=True)
class FastenerProfile:
    family: str
    nominal_unit_system: str
    diameter: str | None = None
    thread_standard: str | None = None
    thread_pitch_tpi: int | None = None
    thread_pitch_mm: float | None = None
    length: str | None = None
    head_type: str | None = None
    material_family: str | None = None
    finish: str | None = None


@dataclass(slots=True)
class Pricing:
    item_total: float
    shipping: float = 0.0
    fees: float = 0.0
    tariff_status: str | None = None


@dataclass(slots=True)
class Availability:
    estimated_arrival_date: date | None = None
    stock_status: str | None = None


@dataclass(slots=True)
class SupplierCandidate:
    vendor: str
    attributes: dict[str, Any]
    pricing: Pricing | None = None
    availability: Availability | None = None
    trust_tier: TrustTier | None = None
    source_tier: str | None = None
    listing_url: str | None = None
    moq: int = 1
    country_of_origin: str | None = None


@dataclass(slots=True)
class EvaluatedCandidate:
    candidate: SupplierCandidate
    match_type: MatchType
    confidence: float
    deadline_status: DeadlineStatus | None
    delivered_total: float | None
    effective_unit_cost: float | None
    trust_tier: TrustTier
    matched_fields: list[str] = field(default_factory=list)
    missing_or_unverified_fields: list[str] = field(default_factory=list)
    explanation: str = ""


@dataclass(slots=True)
class RankedResults:
    deadline_feasible_results: list[EvaluatedCandidate]
    missed_deadline_results: list[EvaluatedCandidate]
