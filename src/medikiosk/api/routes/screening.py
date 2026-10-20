"""Cardiovascular screening route for the MediKiosk 2.0 vertical slice."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends

from medikiosk.api.dependencies.auth import require_kiosk_or_clinician
from medikiosk.api.dependencies.container import (
    get_doctor_repo_dep,
    get_package_catalog_dep,
    get_screening_dep,
)
from medikiosk.api.schemas.screening import (
    CardiovascularReferralResponse,
    CardiovascularScreeningRequest,
)
from medikiosk.domain.contracts.cardiovascular import CardiovascularScreeningResult
from medikiosk.domain.contracts.package import PackageCategory
from medikiosk.domain.referral_matcher import match_cardiovascular_referral
from medikiosk.ports.doctor import DoctorRepository
from medikiosk.ports.package import PackageCatalogPort
from medikiosk.ports.screening import CardiovascularScreeningPort

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/screening", tags=["screening"])

DoctorRepoDep = Annotated[DoctorRepository, Depends(get_doctor_repo_dep)]
PackageRepoDep = Annotated[PackageCatalogPort, Depends(get_package_catalog_dep)]


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


@router.post("/cardiovascular/referral", response_model=CardiovascularReferralResponse)
async def cardiovascular_referral(
    body: CardiovascularScreeningRequest,
    _current_user: Annotated[dict[str, object], Depends(require_kiosk_or_clinician)],
    screening: Annotated[CardiovascularScreeningPort, Depends(get_screening_dep)],
    doctor_repo: DoctorRepoDep,
    package_repo: PackageRepoDep,
) -> CardiovascularReferralResponse:
    """Return local cardiology candidates for explicit clinician review.

    This endpoint does not select a doctor, reserve a package, allocate an
    emergency resource, or claim live hospital capacity.
    """
    screening_result = screening.predict(body.features)
    doctors = await doctor_repo.list_by_department("Cardiology")
    packages = await package_repo.list_packages("Cardiology", PackageCategory.CARDIAC)
    recommendation = match_cardiovascular_referral(
        screening_result,
        doctors,
        packages,
        preferred_language=body.preferred_language,
    )
    log.info(
        "cardiovascular_referral_recommendation_created",
        session_id=str(body.session_id) if body.session_id else None,
        reason_code=recommendation.reason_code,
        doctor_count=len(recommendation.doctor_ids),
        package_count=len(recommendation.package_ids),
    )
    return CardiovascularReferralResponse(
        screening=screening_result,
        recommendation=recommendation,
        session_id=body.session_id,
    )
