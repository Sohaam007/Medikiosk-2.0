"""Application service for clinician-controlled referral workflow outcomes."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Final

from medikiosk.domain.contracts import (
    AuditEvent,
    AuditEventType,
    ReferralCandidateType,
    ReferralOutcome,
    ReferralOutcomeStatus,
)
from medikiosk.domain.errors import (
    AuthorizationError,
    CriticalVetoError,
    ReferralOutcomeConflictError,
    ReferralOutcomeNotFoundError,
    SessionNotFoundError,
    StorageError,
    ValidationError,
)
from medikiosk.domain.referral_outcomes import validate_transition
from medikiosk.ports.audit import AuditRepository
from medikiosk.ports.cache import CachePort
from medikiosk.ports.database import ReferralOutcomeRepository, SessionRepository

CLINICIAN_ROLES: Final[frozenset[str]] = frozenset({"Triage_Nurse", "Attending_Physician"})
_CRITICAL_PRIORITIES: Final[frozenset[str]] = frozenset({"critical", "immediate", "red"})


class ReferralOutcomeService:
    """Coordinate referral outcome persistence, veto checks, and audit writes."""

    def __init__(
        self,
        outcome_repo: ReferralOutcomeRepository,
        session_repo: SessionRepository,
        audit_repo: AuditRepository,
        cache: CachePort | None = None,
    ) -> None:
        self._outcome_repo = outcome_repo
        self._session_repo = session_repo
        self._audit_repo = audit_repo
        self._cache = cache

    @staticmethod
    def _require_clinician(actor_role: str) -> None:
        if actor_role not in CLINICIAN_ROLES:
            raise AuthorizationError("Clinician role required")

    async def _ensure_routine_session(self, session_id: uuid.UUID) -> None:
        session = await self._session_repo.get(session_id)
        if session is None:
            raise SessionNotFoundError(f"Session not found: {session_id}")

        if session.news2_risk_band == "HIGH" or (
            session.news2_score is not None and session.news2_score >= 7
        ):
            raise CriticalVetoError("Critical clinical veto blocks routine referral tracking")

        if self._cache is None:
            return

        cached_intake = await self._cache.get(f"intake:{session_id}")
        if cached_intake is None:
            return
        try:
            intake_data = json.loads(cached_intake)
        except json.JSONDecodeError as exc:
            raise StorageError("Unable to read triage state for referral workflow") from exc
        if not isinstance(intake_data, dict):
            raise StorageError("Unable to read triage state for referral workflow")

        alerts = intake_data.get("triage_alerts", [])
        if not isinstance(alerts, list):
            raise StorageError("Unable to read triage state for referral workflow")
        for alert in alerts:
            if not isinstance(alert, dict):
                continue
            priority = alert.get("priority")
            priority_value = str(getattr(priority, "value", priority)).lower()
            if priority_value in _CRITICAL_PRIORITIES:
                raise CriticalVetoError("Critical clinical veto blocks routine referral tracking")

    async def _append_audit(
        self,
        *,
        session_id: uuid.UUID,
        event_type: AuditEventType,
        payload: dict[str, object],
        now: datetime,
    ) -> None:
        sequence_number = await self._audit_repo.get_latest_sequence(session_id) + 1
        await self._audit_repo.append(
            AuditEvent(
                event_id=uuid.uuid4(),
                session_id=session_id,
                event_type=event_type,
                timestamp=now,
                sequence_number=sequence_number,
                payload=payload,
            )
        )

    async def create(
        self,
        *,
        session_id: uuid.UUID,
        candidate_type: ReferralCandidateType,
        candidate_id: uuid.UUID,
        actor_role: str,
        now: datetime,
    ) -> ReferralOutcome:
        """Create a recommended outcome for one local referral candidate."""
        self._require_clinician(actor_role)
        await self._ensure_routine_session(session_id)
        existing = await self._outcome_repo.get_for_candidate(
            session_id, candidate_type, candidate_id
        )
        if existing is not None:
            raise ReferralOutcomeConflictError(
                "Referral candidate already has a workflow outcome for this session"
            )

        outcome = ReferralOutcome(
            outcome_id=uuid.uuid4(),
            session_id=session_id,
            candidate_id=candidate_id,
            candidate_type=candidate_type,
            status=ReferralOutcomeStatus.RECOMMENDED,
            created_at=now,
            updated_at=now,
        )
        await self._outcome_repo.create(outcome)
        await self._append_audit(
            session_id=session_id,
            event_type=AuditEventType.REFERRAL_OUTCOME_CREATED,
            now=now,
            payload={
                "action": "create",
                "actor_role": actor_role,
                "candidate_id": str(candidate_id),
                "candidate_type": candidate_type.value,
                "new_status": outcome.status.value,
                "outcome_id": str(outcome.outcome_id),
            },
        )
        return outcome

    async def get(self, outcome_id: uuid.UUID) -> ReferralOutcome:
        """Read one workflow outcome by opaque ID."""
        outcome = await self._outcome_repo.get(outcome_id)
        if outcome is None:
            raise ReferralOutcomeNotFoundError("Referral outcome not found")
        return outcome

    async def list_for_session(self, session_id: uuid.UUID) -> list[ReferralOutcome]:
        """Read current workflow metadata for one session."""
        await self._ensure_routine_session(session_id)
        return await self._outcome_repo.list_for_session(session_id)

    async def transition(
        self,
        *,
        outcome_id: uuid.UUID,
        target_status: ReferralOutcomeStatus | str,
        actor_role: str,
        now: datetime,
    ) -> ReferralOutcome:
        """Apply one legal workflow transition and append its audit event."""
        self._require_clinician(actor_role)
        try:
            target_status = ReferralOutcomeStatus(target_status)
        except ValueError as exc:
            raise ValidationError("Invalid referral outcome status") from exc
        current = await self.get(outcome_id)
        await self._ensure_routine_session(current.session_id)
        validate_transition(current.status, target_status)

        updated = current.model_copy(update={"status": target_status, "updated_at": now})
        await self._outcome_repo.update(updated)
        await self._append_audit(
            session_id=current.session_id,
            event_type=AuditEventType.REFERRAL_OUTCOME_TRANSITIONED,
            now=now,
            payload={
                "action": "transition",
                "actor_role": actor_role,
                "candidate_id": str(current.candidate_id),
                "candidate_type": current.candidate_type.value,
                "outcome_id": str(current.outcome_id),
                "prior_status": current.status.value,
                "new_status": target_status.value,
            },
        )
        return updated
