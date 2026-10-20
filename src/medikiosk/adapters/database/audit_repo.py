"""SQLAlchemy AuditRepository implementation. APPEND-ONLY.

This class has NO update() or delete() methods. The audit trail is
immutable once written. AuditError is raised on any write failure and
the calling service MUST NOT proceed if an audit write fails.
"""

from __future__ import annotations

import json
from datetime import UTC
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from medikiosk.adapters.database.models import AuditEventModel
from medikiosk.adapters.logging import get_logger
from medikiosk.domain.audit_chain import GENESIS_HASH, calculate_event_hash
from medikiosk.domain.contracts import AuditEvent, AuditEventType
from medikiosk.domain.errors import AuditError

log = get_logger(__name__)


class SQLAuditRepository:
    """SQLAlchemy-backed AuditRepository. Strictly APPEND-ONLY.

    This class deliberately exposes NO update() or delete() methods.

    Args:
        session: The AsyncSession to use for DB operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_model(event: AuditEvent) -> AuditEventModel:
        """Convert domain AuditEvent to ORM model."""
        return AuditEventModel(
            event_id=str(event.event_id),
            session_id=str(event.session_id),
            event_type=event.event_type.value,
            timestamp=event.timestamp,
            payload=json.dumps(event.payload),
            sequence_number=event.sequence_number,
            prev_hash=event.prev_hash,
            event_hash=event.event_hash,
        )

    @staticmethod
    def _to_domain(model: AuditEventModel) -> AuditEvent:
        """Convert ORM model to domain AuditEvent."""
        timestamp = (
            model.timestamp
            if model.timestamp.tzinfo is not None
            else model.timestamp.replace(tzinfo=UTC)
        )
        return AuditEvent(
            event_id=UUID(model.event_id),
            session_id=UUID(model.session_id),
            event_type=AuditEventType(model.event_type),
            timestamp=timestamp,
            payload=json.loads(model.payload),
            sequence_number=model.sequence_number,
            prev_hash=model.prev_hash,
            event_hash=model.event_hash,
        )

    async def append(self, event: AuditEvent) -> AuditEvent:
        """Append a new audit event. The ONLY write method."""
        try:
            persisted_event = event
            if not event.event_hash:
                result = await self._session.execute(
                    select(AuditEventModel)
                    .where(AuditEventModel.session_id == str(event.session_id))
                    .order_by(AuditEventModel.sequence_number.desc())
                    .limit(1)
                )
                prev_model = result.scalar_one_or_none()
                if prev_model is not None and prev_model.event_hash:
                    prev_hash = prev_model.event_hash
                else:
                    prev_hash = event.prev_hash if event.prev_hash != ("0" * 64) else GENESIS_HASH

                ts_iso = event.timestamp.isoformat()
                computed_hash = calculate_event_hash(
                    prev_hash=prev_hash,
                    session_id=event.session_id,
                    seq=event.sequence_number,
                    event_type=event.event_type.value,
                    timestamp_iso=ts_iso,
                    metadata_keys_sorted=event.payload,
                )
                persisted_event = AuditEvent(
                    event_id=event.event_id,
                    session_id=event.session_id,
                    event_type=event.event_type,
                    timestamp=event.timestamp,
                    payload=event.payload,
                    sequence_number=event.sequence_number,
                    prev_hash=prev_hash,
                    event_hash=computed_hash,
                )

            model = self._to_model(persisted_event)
            self._session.add(model)
            await self._session.flush()
            log.info(
                "audit_appended",
                session_id=str(persisted_event.session_id),
                event_type=persisted_event.event_type.value,
                seq=persisted_event.sequence_number,
            )
            return persisted_event
        except SQLAlchemyError as exc:
            raise AuditError(
                f"CRITICAL: audit write failed ({type(exc).__name__}). "
                "Caller must not proceed without audit trail."
            ) from exc

    async def list_for_session(
        self,
        session_id: UUID,
        *,
        event_type: AuditEventType | None = None,
    ) -> list[AuditEvent]:
        """Retrieve all events for a session, sorted by sequence_number."""
        try:
            query = select(AuditEventModel).where(AuditEventModel.session_id == str(session_id))
            if event_type is not None:
                query = query.where(AuditEventModel.event_type == event_type.value)
            query = query.order_by(AuditEventModel.sequence_number)
            result = await self._session.execute(query)
            return [self._to_domain(m) for m in result.scalars().all()]
        except SQLAlchemyError as exc:
            raise AuditError(f"Failed to list audit events: {type(exc).__name__}") from exc

    async def get_latest_sequence(self, session_id: UUID) -> int:
        """Get highest sequence_number for a session, or -1 if none."""
        try:
            result = await self._session.execute(
                select(func.max(AuditEventModel.sequence_number)).where(
                    AuditEventModel.session_id == str(session_id)
                )
            )
            value = result.scalar_one_or_none()
            return int(value) if value is not None else -1
        except SQLAlchemyError as exc:
            raise AuditError(f"Failed to get sequence: {type(exc).__name__}") from exc
