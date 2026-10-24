"""HTTP schemas for clinician referral workflow outcomes."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from medikiosk.domain.contracts import (
    ReferralCandidateType,
    ReferralOutcome,
    ReferralOutcomeStatus,
)


class ReferralOutcomeCreateRequest(BaseModel):
    """Create a workflow record for one local referral candidate."""

    session_id: UUID
    candidate_id: UUID
    candidate_type: ReferralCandidateType


class ReferralOutcomeTransitionRequest(BaseModel):
    """Move one referral workflow record to its next legal status."""

    status: ReferralOutcomeStatus


class ReferralOutcomeResponse(BaseModel):
    """Opaque workflow metadata only; no PHI or clinical outcome fields."""

    outcome_id: UUID
    session_id: UUID
    candidate_id: UUID
    candidate_type: ReferralCandidateType
    status: ReferralOutcomeStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, outcome: ReferralOutcome) -> ReferralOutcomeResponse:
        return cls.model_validate(outcome.model_dump())


class ReferralOutcomeListResponse(BaseModel):
    """Deterministically ordered workflow records for one session."""

    session_id: UUID
    items: list[ReferralOutcomeResponse]
    total_count: int = Field(ge=0)
