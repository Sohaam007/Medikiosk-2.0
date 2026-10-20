from medikiosk.adapters.cardiovision import CardioVisionAdapter
from medikiosk.adapters.doctor.seed_data import SEED_DOCTORS
from medikiosk.adapters.package.seed_data import SEED_PACKAGES
from medikiosk.domain.contracts.doctor import DoctorAvailabilityStatus
from medikiosk.domain.referral_matcher import match_cardiovascular_referral


def test_positive_screen_returns_available_cardiology_candidates() -> None:
    result = CardioVisionAdapter().predict({"Age": 72, "HTN": 1, "Typical Chest Pain": 1})

    recommendation = match_cardiovascular_referral(
        result,
        SEED_DOCTORS,
        SEED_PACKAGES,
        preferred_language="hi-IN",
    )

    assert recommendation.reason_code == "CARDIO_SCREEN_REVIEW"
    assert recommendation.priority == "urgent"
    assert str(SEED_DOCTORS[0].doctor_id) in {str(value) for value in recommendation.doctor_ids}
    assert recommendation.package_ids == [SEED_PACKAGES[0].package_id]
    assert recommendation.requires_clinician_review is True
    assert "CAD_SCREEN_POSITIVE" in recommendation.matched_signals


def test_low_risk_screen_does_not_force_a_referral() -> None:
    result = CardioVisionAdapter().predict(
        {"Age": 30, "HTN": 0, "DM": 0, "Typical Chest Pain": 0, "BP": 120, "EF-TTE": 60}
    )

    recommendation = match_cardiovascular_referral(result, SEED_DOCTORS, SEED_PACKAGES)

    assert recommendation.reason_code == "NO_AUTOMATIC_REFERRAL"
    assert recommendation.doctor_ids == []
    assert recommendation.package_ids == []
    assert recommendation.requires_clinician_review is True


def test_unavailable_doctors_are_excluded_without_mutating_catalogues() -> None:
    unavailable = SEED_DOCTORS[0].model_copy(
        update={"availability_status": DoctorAvailabilityStatus.ON_LEAVE}
    )
    result = CardioVisionAdapter().predict({"Age": 72, "HTN": 1, "Typical Chest Pain": 1})

    recommendation = match_cardiovascular_referral(
        result,
        [unavailable, *SEED_DOCTORS[1:]],
        SEED_PACKAGES,
    )

    assert recommendation.doctor_ids == []
    assert unavailable.availability_status.value == "on_leave"
