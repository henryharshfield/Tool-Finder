from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from tool_finder.service import evaluate_candidates, source_request_from_dict


class SourceRequestPayload(BaseModel):
    requested_quantity: int
    needed_by_date: str | None = None
    today: str | None = None
    country_filter: str | None = None
    shipping_destination: str | None = None
    match_mode: str = "exact_preferred_substitutes_allowed"
    input_type: str | None = None
    raw_input: str | None = None


class SourceProfilePayload(BaseModel):
    fastener_family: str
    nominal_unit_system: str
    diameter: str | None = None
    thread_standard: str | None = None
    thread_pitch_tpi: int | None = None
    thread_pitch_mm: float | None = None
    length: str | None = None
    head_type: str | None = None
    material_family: str | None = None
    finish: str | None = None


class EvaluateRequest(BaseModel):
    source_request: SourceRequestPayload = Field(..., description="Normalized source request")
    source_profile: SourceProfilePayload = Field(..., description="Normalized source profile")
    candidates: list[dict] = Field(default_factory=list, description="Normalized or raw candidate dictionaries")


class ResultItem(BaseModel):
    vendor: str
    match_type: str
    confidence: float
    deadline_status: str | None
    delivered_total: float | None
    effective_unit_cost: float | None
    vendor_trust: str
    country_of_origin: str | None
    matched_fields: list[str]
    unverified_or_missing_fields: list[str]
    explanation: str


class EvaluateResponse(BaseModel):
    deadline_feasible_results: list[ResultItem]
    missed_deadline_results: list[ResultItem]


app = FastAPI(title="Tool Finder V1 Backend", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(payload: EvaluateRequest) -> EvaluateResponse:
    request = source_request_from_dict(payload.source_request.model_dump())
    ranked = evaluate_candidates(request, payload.source_profile.model_dump(), payload.candidates)

    def serialize(item) -> ResultItem:
        return ResultItem(
            vendor=item.candidate.vendor,
            match_type=item.match_type.value,
            confidence=item.confidence,
            deadline_status=item.deadline_status.value if item.deadline_status else None,
            delivered_total=item.delivered_total,
            effective_unit_cost=item.effective_unit_cost,
            vendor_trust=item.trust_tier.value,
            country_of_origin=item.candidate.country_of_origin,
            matched_fields=item.matched_fields,
            unverified_or_missing_fields=item.missing_or_unverified_fields,
            explanation=item.explanation,
        )

    return EvaluateResponse(
        deadline_feasible_results=[serialize(x) for x in ranked.deadline_feasible_results],
        missed_deadline_results=[serialize(x) for x in ranked.missed_deadline_results],
    )
