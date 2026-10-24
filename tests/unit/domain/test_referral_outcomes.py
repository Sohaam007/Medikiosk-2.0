from datetime import UTC, datetime
from uuid import uuid4

import pytest

from medikiosk.domain.contracts import (
    ReferralCandidateType,
    ReferralOutcome,
    ReferralOutcomeStatus,
)
from medikiosk.domain.errors import ValidationError
from medikiosk.domain.referral_outcomes import validate_transition


def test_referral_outcome_contract_preserves_opaque_workflow_metadata() -> None:
    now = datetime(2026, 10, 25, 12, 0, tzinfo=UTC)
    outcome = ReferralOutcome(
        outcome_id=uuid4(),
        session_id=uuid4(),
        candidate_id=uuid4(),
        candidate_type=ReferralCandidateType.DOCTOR,
        status=ReferralOutcomeStatus.RECOMMENDED,
        created_at=now,
        updated_at=now,
    )

    assert outcome.status is ReferralOutcomeStatus.RECOMMENDED
    assert outcome.candidate_type is ReferralCandidateType.DOCTOR
    assert outcome.model_dump().keys() == {
        "outcome_id",
        "session_id",
        "candidate_id",
        "candidate_type",
        "status",
        "created_at",
        "updated_at",
    }


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (ReferralOutcomeStatus.RECOMMENDED, ReferralOutcomeStatus.REVIEWED),
        (ReferralOutcomeStatus.REVIEWED, ReferralOutcomeStatus.CONTACTED),
        (ReferralOutcomeStatus.CONTACTED, ReferralOutcomeStatus.ATTENDED),
        (ReferralOutcomeStatus.CONTACTED, ReferralOutcomeStatus.DECLINED),
    ],
)
def test_allowed_referral_outcome_transitions_are_accepted(
    current: ReferralOutcomeStatus,
    target: ReferralOutcomeStatus,
) -> None:
    validate_transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (ReferralOutcomeStatus.RECOMMENDED, ReferralOutcomeStatus.CONTACTED),
        (ReferralOutcomeStatus.REVIEWED, ReferralOutcomeStatus.ATTENDED),
        (ReferralOutcomeStatus.CONTACTED, ReferralOutcomeStatus.RECOMMENDED),
        (ReferralOutcomeStatus.ATTENDED, ReferralOutcomeStatus.DECLINED),
        (ReferralOutcomeStatus.DECLINED, ReferralOutcomeStatus.REVIEWED),
        (ReferralOutcomeStatus.RECOMMENDED, ReferralOutcomeStatus.RECOMMENDED),
    ],
)
def test_invalid_backward_skipped_and_terminal_transitions_are_rejected(
    current: ReferralOutcomeStatus,
    target: ReferralOutcomeStatus,
) -> None:
    with pytest.raises(ValidationError, match="Invalid referral outcome transition"):
        validate_transition(current, target)
