"""Cardiovascular screening route for the MediKiosk 2.0 vertical slice."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends

from medikiosk.api.dependencies.auth import require_kiosk_or_clinician
from medikiosk.api.dependencies.container import get_screening_dep
from medikiosk.api.schemas.screening import CardiovascularScreeningRequest
from medikiosk.domain.contracts.cardiovascular import CardiovascularScreeningResult
from medikiosk.ports.screening import CardiovascularScreeningPort

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/screening", tags=["screening"])


@router.post("/cardiovascular", response_model=CardiovascularScreeningResult)
def cardiovascular_screening(
    body: CardiovascularScreeningRequest,
    _current_user: Annotated[dict[str, object], Depends(require_kiosk_or_clinician)],
    screening: Annotated[CardiovascularScreeningPort, Depends(get_screening_dep)],
) -> CardiovascularScreeningResult:
    """Screen cardiovascular risk and return a clinician-reviewable result.

    Only the opaque session identifier is included in telemetry. The feature
    dictionary is never logged because it may contain sensitive clinical data.
    """
    log.info(
        "cardiovascular_screening_requested",
        session_id=str(body.session_id) if body.session_id else None,
    )
    return screening.predict(body.features)
