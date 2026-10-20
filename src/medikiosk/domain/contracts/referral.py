"""Contracts for clinician-reviewed referral recommendations."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReferralRecommendation(BaseModel):
    """Deterministic candidate IDs; this is not an appointment or diagnosis."""

    model_config = ConfigDict(frozen=True)

    department: str | None = None
    doctor_ids: list[UUID] = Field(default_factory=list)
    package_ids: list[UUID] = Field(default_factory=list)
    matched_signals: list[str] = Field(default_factory=list)
    reason_code: str
    priority: str
    requires_clinician_review: bool = True
    screening_disclaimer: str = (
        "Screening support only; clinician review is required before referral action."
    )
