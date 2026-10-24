"""Clinician-only local referral workflow outcome routes."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Query, status

from medikiosk.api.dependencies.auth import require_clinician
from medikiosk.api.dependencies.container import get_referral_outcome_service_dep
from medikiosk.api.schemas.referral_outcomes import (
    ReferralOutcomeCreateRequest,
    ReferralOutcomeListResponse,
    ReferralOutcomeResponse,
    ReferralOutcomeTransitionRequest,
)
from medikiosk.domain.contracts import ReferralOutcomeStatus
from medikiosk.services.referral_outcome_service import ReferralOutcomeService

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/clinician/referral-outcomes", tags=["clinician"])

_ClinicianDep = Annotated[dict[str, object], Depends(require_clinician)]
_ServiceDep = Annotated[ReferralOutcomeService, Depends(get_referral_outcome_service_dep)]


@router.post("", response_model=ReferralOutcomeResponse, status_code=status.HTTP_201_CREATED)
async def create_referral_outcome(
    body: ReferralOutcomeCreateRequest,
    current_user: _ClinicianDep,
    service: _ServiceDep,
) -> ReferralOutcomeResponse:
    """Create a recommended, non-binding referral workflow record."""
    outcome = await service.create(
        session_id=body.session_id,
        candidate_type=body.candidate_type,
        candidate_id=body.candidate_id,
        actor_role=str(current_user["role"]),
        now=datetime.now(UTC),
    )
    log.info("referral_outcome_created", outcome_id=str(outcome.outcome_id))
    return ReferralOutcomeResponse.from_domain(outcome)


@router.get("", response_model=ReferralOutcomeListResponse)
async def list_referral_outcomes(
    session_id: Annotated[UUID, Query()],
    _current_user: _ClinicianDep,
    service: _ServiceDep,
) -> ReferralOutcomeListResponse:
    """List opaque workflow metadata for one session."""
    outcomes = await service.list_for_session(session_id)
    return ReferralOutcomeListResponse(
        session_id=session_id,
        items=[ReferralOutcomeResponse.from_domain(item) for item in outcomes],
        total_count=len(outcomes),
    )


@router.get("/{outcome_id}", response_model=ReferralOutcomeResponse)
async def get_referral_outcome(
    outcome_id: UUID,
    _current_user: _ClinicianDep,
    service: _ServiceDep,
) -> ReferralOutcomeResponse:
    """Read one opaque workflow record."""
    outcome = await service.get(outcome_id)
    return ReferralOutcomeResponse.from_domain(outcome)


@router.post("/{outcome_id}/transition", response_model=ReferralOutcomeResponse)
async def transition_referral_outcome(
    outcome_id: UUID,
    body: ReferralOutcomeTransitionRequest,
    current_user: _ClinicianDep,
    service: _ServiceDep,
) -> ReferralOutcomeResponse:
    """Apply one legal clinician-controlled workflow transition."""
    outcome = await service.transition(
        outcome_id=outcome_id,
        target_status=body.status,
        actor_role=str(current_user["role"]),
        now=datetime.now(UTC),
    )
    log.info(
        "referral_outcome_transitioned",
        outcome_id=str(outcome.outcome_id),
        status=ReferralOutcomeStatus(outcome.status).value,
    )
    return ReferralOutcomeResponse.from_domain(outcome)
