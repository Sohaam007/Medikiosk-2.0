"""Pure CardioVision-to-referral policy.

This policy deliberately produces candidates, not selections. Emergency triage
and resource allocation remain separate authoritative safety paths.
"""

from __future__ import annotations

from collections.abc import Sequence

from medikiosk.domain.contracts import (
    CardiovascularScreeningResult,
    DoctorAvailabilityStatus,
    DoctorProfile,
    HospitalPackage,
    PackageCategory,
    ReferralRecommendation,
)


def match_cardiovascular_referral(
    result: CardiovascularScreeningResult,
    doctors: Sequence[DoctorProfile],
    packages: Sequence[HospitalPackage],
    preferred_language: str | None = None,
) -> ReferralRecommendation:
    """Return stable cardiology candidates for clinician review.

    A positive screening signal yields an urgent review recommendation, never
    an emergency escalation. Critical disposition must come from the server-
    side veto engine using symptoms or physiological deterioration.
    """
    signals = _screening_signals(result)
    if not signals:
        return ReferralRecommendation(
            reason_code="NO_AUTOMATIC_REFERRAL",
            priority="routine",
            matched_signals=["SCREENING_BELOW_REFERRAL_THRESHOLD"],
        )

    cardiologists = [
        doctor
        for doctor in doctors
        if doctor.department.casefold() == "cardiology"
        and doctor.availability_status == DoctorAvailabilityStatus.AVAILABLE
    ]
    cardiologists.sort(key=lambda doctor: _doctor_sort_key(doctor, preferred_language))
    cardiac_packages = [
        package
        for package in packages
        if package.is_active
        and package.category == PackageCategory.CARDIAC
        and package.department.casefold() == "cardiology"
    ]
    cardiac_packages.sort(key=lambda package: str(package.package_id))
    return ReferralRecommendation(
        department="Cardiology",
        doctor_ids=[doctor.doctor_id for doctor in cardiologists],
        package_ids=[package.package_id for package in cardiac_packages],
        matched_signals=signals,
        reason_code="CARDIO_SCREEN_REVIEW",
        priority="urgent",
    )


def _screening_signals(result: CardiovascularScreeningResult) -> list[str]:
    signals: list[str] = []
    if result.cad.label == 1:
        signals.append("CAD_SCREEN_POSITIVE")
    for vessel, risk in sorted(result.vessels.items()):
        if risk.label == 1:
            signals.append(f"{vessel.upper()}_SCREEN_POSITIVE")
    return signals


def _doctor_sort_key(
    doctor: DoctorProfile, preferred_language: str | None
) -> tuple[int, float, int, str]:
    language_match = 0
    if preferred_language:
        requested = preferred_language.casefold().split("-")[0]
        language_match = int(
            any(language.casefold().split("-")[0] == requested for language in doctor.languages)
        )
    return (
        -language_match,
        -(doctor.rating or 0.0),
        -doctor.experience_years,
        str(doctor.doctor_id),
    )
