from datetime import UTC, datetime
from uuid import uuid4

import pytest

from medikiosk.domain.contracts import (
    AuditEvent,
    InformantType,
    ReferralCandidateType,
    SessionState,
    SessionStatus,
)
from medikiosk.domain.errors import CriticalVetoError, ReferralOutcomeConflictError
from medikiosk.services.referral_outcome_service import ReferralOutcomeService


NOW = datetime(2026, 10, 25, 12, 0, tzinfo=UTC)


class FakeOutcomeRepository:
    def __init__(self) -> None:
        self.items = {}

    async def create(self, outcome):
        self.items[str(outcome.outcome_id)] = outcome
        return outcome

    async def get(self, outcome_id):
        return self.items.get(str(outcome_id))

    async def update(self, outcome):
        self.items[str(outcome.outcome_id)] = outcome
        return outcome

    async def get_for_candidate(self, session_id, candidate_type, candidate_id):
        return next(
            (
                item
                for item in self.items.values()
                if item.session_id == session_id
                and item.candidate_type == candidate_type
                and item.candidate_id == candidate_id
            ),
            None,
        )

    async def list_for_session(self, session_id):
        return sorted(
            (item for item in self.items.values() if item.session_id == session_id),
            key=lambda item: (item.created_at, str(item.outcome_id)),
        )


class FakeSessionRepository:
    def __init__(self, session: SessionState) -> None:
        self.session = session

    async def get(self, session_id):
        return self.session if self.session.session_id == session_id else None


class FakeAuditRepository:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    async def append(self, event):
        self.events.append(event)
        return event

    async def get_latest_sequence(self, session_id):
        events = [event for event in self.events if event.session_id == session_id]
        return max((event.sequence_number for event in events), default=-1)


def make_session(*, news2_score: int | None = None, news2_risk_band: str | None = None):
    return SessionState(
        session_id=uuid4(),
        patient_language="en",
        created_at=NOW,
        status=SessionStatus.ACTIVE,
        consent_status=True,
        intake_progress=1.0,
        informant_type=InformantType.PATIENT,
        news2_score=news2_score,
        news2_risk_band=news2_risk_band,
    )


@pytest.mark.asyncio
async def test_create_and_transition_append_opaque_audit_events() -> None:
    session = make_session()
    outcome_repo = FakeOutcomeRepository()
    audit_repo = FakeAuditRepository()
    service = ReferralOutcomeService(
        outcome_repo,
        FakeSessionRepository(session),
        audit_repo,
    )
    candidate_id = uuid4()

    created = await service.create(
        session_id=session.session_id,
        candidate_type=ReferralCandidateType.DOCTOR,
        candidate_id=candidate_id,
        actor_role="Triage_Nurse",
        now=NOW,
    )
    transitioned = await service.transition(
        outcome_id=created.outcome_id,
        target_status="reviewed",
        actor_role="Attending_Physician",
        now=NOW,
    )

    assert transitioned.status.value == "reviewed"
    assert [event.event_type.value for event in audit_repo.events] == [
        "referral_outcome_created",
        "referral_outcome_transitioned",
    ]
    assert audit_repo.events[0].payload == {
        "action": "create",
        "actor_role": "Triage_Nurse",
        "candidate_id": str(candidate_id),
        "candidate_type": "doctor",
        "new_status": "recommended",
        "outcome_id": str(created.outcome_id),
    }
    assert audit_repo.events[1].payload["prior_status"] == "recommended"
    assert audit_repo.events[1].payload["new_status"] == "reviewed"


@pytest.mark.asyncio
async def test_duplicate_candidate_is_rejected() -> None:
    session = make_session()
    outcome_repo = FakeOutcomeRepository()
    service = ReferralOutcomeService(
        outcome_repo,
        FakeSessionRepository(session),
        FakeAuditRepository(),
    )
    candidate_id = uuid4()

    await service.create(
        session_id=session.session_id,
        candidate_type=ReferralCandidateType.PACKAGE,
        candidate_id=candidate_id,
        actor_role="Triage_Nurse",
        now=NOW,
    )

    with pytest.raises(ReferralOutcomeConflictError):
        await service.create(
            session_id=session.session_id,
            candidate_type=ReferralCandidateType.PACKAGE,
            candidate_id=candidate_id,
            actor_role="Triage_Nurse",
            now=NOW,
        )


@pytest.mark.asyncio
async def test_critical_veto_session_cannot_create_or_transition() -> None:
    session = make_session(news2_score=7, news2_risk_band="HIGH")
    service = ReferralOutcomeService(
        FakeOutcomeRepository(),
        FakeSessionRepository(session),
        FakeAuditRepository(),
    )

    with pytest.raises(CriticalVetoError):
        await service.create(
            session_id=session.session_id,
            candidate_type=ReferralCandidateType.DOCTOR,
            candidate_id=uuid4(),
            actor_role="Triage_Nurse",
            now=NOW,
        )
