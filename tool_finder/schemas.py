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


TRUST_SCORES = {"High": 3, "Medium": 2, "Low": 1}


@dataclass(frozen=True)
class SourceRequest:
    requested_quantity: int
    needed_by_date: date | None = None
    shipping_destination: str | None = None
    match_mode: MatchMode = MatchMode.EXACT_ONLY
    country_filter: str | None = None
    today: date | None = None


@dataclass(frozen=True)
class FastenerProfile:
    family: str
    nominal_unit_system: str
    diameter: str
    thread_standard: str
    thread_pitch_tpi: int | None = None
    thread_pitch_mm: float | None = None
    length: str | None = None
    head_type: str | None = None
    drive_style: str | None = None
    material_family: str | None = None
    finish: str | None = None
    mpn: str | None = None


@dataclass(frozen=True)
class Pricing:
    item_total: float | None = None
    shipping: float | None = None
    fees: float | None = None
    delivered_total: float | None = None
    tariff_status: str | None = None


@dataclass(frozen=True)
class Availability:
    estimated_arrival_date: date | None = None
    stock_status: str | None = None


@dataclass(frozen=True)
class Candidate:
    vendor: str
    attributes: dict[str, Any]
    trust_tier: str = "Medium"
    source_tier: str | None = None
    listing_url: str | None = None
    pricing: Pricing | None = None
    availability: Availability | None = None
    moq: int = 1
    country_of_origin: str | None = None


@dataclass
class RankedResult:
    candidate: Candidate
    match_type: MatchType
    deadline_status: DeadlineStatus
    delivered_total: float
    effective_unit_cost: float
    trust_score: int
    trust_override_applied: bool = False
    matched_fields: list[str] = field(default_factory=list)
    missing_or_unverified_fields: list[str] = field(default_factory=list)
    explanation: str = ""


@dataclass
class RankingOutput:
    deadline_feasible_results: list[RankedResult]
    missed_deadline_results: list[RankedResult]


REQUIRED_EXACT_FIELDS = (
    "family",
    "nominal_unit_system",
    "diameter",
    "thread_standard",
    "length",
    "head_type",
    "material_family",
)
