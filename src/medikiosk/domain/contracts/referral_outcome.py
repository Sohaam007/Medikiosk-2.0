"""Contracts for clinician-controlled referral workflow outcomes."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReferralCandidateType(str, Enum):
    """The local catalog type represented by a referral candidate ID."""

    DOCTOR = "doctor"
    PACKAGE = "package"


class ReferralOutcomeStatus(str, Enum):
    """Workflow metadata for a non-binding referral candidate."""

    RECOMMENDED = "recommended"
    REVIEWED = "reviewed"
    CONTACTED = "contacted"
    ATTENDED = "attended"
    DECLINED = "declined"


class ReferralOutcome(BaseModel):
    """Opaque referral workflow state; never a clinical or treatment outcome."""

    model_config = ConfigDict(frozen=True)

    outcome_id: UUID
    session_id: UUID
    candidate_id: UUID
    candidate_type: ReferralCandidateType
    status: ReferralOutcomeStatus
    created_at: datetime
    updated_at: datetime
