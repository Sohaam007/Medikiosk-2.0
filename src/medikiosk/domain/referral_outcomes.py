"""Pure referral workflow transition policy."""

from __future__ import annotations

from medikiosk.domain.contracts import ReferralOutcomeStatus
from medikiosk.domain.errors import ValidationError

_VALID_TRANSITIONS: dict[ReferralOutcomeStatus, frozenset[ReferralOutcomeStatus]] = {
    ReferralOutcomeStatus.RECOMMENDED: frozenset({ReferralOutcomeStatus.REVIEWED}),
    ReferralOutcomeStatus.REVIEWED: frozenset({ReferralOutcomeStatus.CONTACTED}),
    ReferralOutcomeStatus.CONTACTED: frozenset(
        {ReferralOutcomeStatus.ATTENDED, ReferralOutcomeStatus.DECLINED}
    ),
    ReferralOutcomeStatus.ATTENDED: frozenset(),
    ReferralOutcomeStatus.DECLINED: frozenset(),
}


def validate_transition(
    current: ReferralOutcomeStatus,
    target: ReferralOutcomeStatus,
) -> None:
    """Reject same, backward, skipped, and terminal-state transitions."""
    if target not in _VALID_TRANSITIONS[current]:
        raise ValidationError("Invalid referral outcome transition")
