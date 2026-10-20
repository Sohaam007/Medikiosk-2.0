"""Integration tests for Phase 3 adapter persistence and cryptographic audit hash chaining.

Tests SQLSessionRepository field round-tripping and SQLAuditRepository automated Merkle linking.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from medikiosk.adapters.database.audit_repo import SQLAuditRepository
from medikiosk.adapters.database.models import Base
from medikiosk.adapters.database.session_repo import SQLSessionRepository
from medikiosk.domain.audit_chain import GENESIS_HASH, verify_audit_chain
from medikiosk.domain.contracts import (
    AuditEvent,
    AuditEventType,
    InformantType,
    SessionState,
    SessionStatus,
)


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_session_repo_phase3_fields_roundtrip(db_session) -> None:
    repo = SQLSessionRepository(db_session)
    sid = uuid.uuid4()
    now = datetime.now(UTC)

    labs_json = json.dumps([{"code": "ECG-01", "name": "STAT 12-Lead ECG"}])
    session_in = SessionState(
        session_id=sid,
        patient_language="hi",
        created_at=now,
        status=SessionStatus.ACTIVE,
        consent_status=True,
        informant_type=InformantType.PATIENT,
        recommended_labs_json=labs_json,
        allocated_resource_id="RESUS-BAY-01",
        porter_ticket_id="PORTER-1234",
    )

    created = await repo.create(session_in)
    assert created.recommended_labs_json == labs_json
    assert created.allocated_resource_id == "RESUS-BAY-01"
    assert created.porter_ticket_id == "PORTER-1234"

    fetched = await repo.get(sid)
    assert fetched is not None
    assert fetched.recommended_labs_json == labs_json
    assert fetched.allocated_resource_id == "RESUS-BAY-01"
    assert fetched.porter_ticket_id == "PORTER-1234"

    # Test update of phase 3 fields
    updated_labs = json.dumps([{"code": "LAB-CBC", "name": "CBC with Platelets"}])
    session_updated = SessionState(
        session_id=sid,
        patient_language="hi",
        created_at=now,
        status=SessionStatus.COMPLETED,
        consent_status=True,
        informant_type=InformantType.PATIENT,
        recommended_labs_json=updated_labs,
        allocated_resource_id="ISO-ROOM-01",
        porter_ticket_id="PORTER-9999",
    )
    await repo.update(session_updated)

    refetched = await repo.get(sid)
    assert refetched is not None
    assert refetched.status == SessionStatus.COMPLETED
    assert refetched.recommended_labs_json == updated_labs
    assert refetched.allocated_resource_id == "ISO-ROOM-01"
    assert refetched.porter_ticket_id == "PORTER-9999"


@pytest.mark.asyncio
async def test_audit_repo_automated_merkle_chaining(db_session) -> None:
    audit_repo = SQLAuditRepository(db_session)
    sid = uuid.uuid4()
    now = datetime(2026, 10, 18, 14, 0, 0, tzinfo=UTC)

    # 1. Append first event without explicit hash
    ev0 = AuditEvent(
        event_id=uuid.uuid4(),
        session_id=sid,
        event_type=AuditEventType.SESSION_CREATED,
        timestamp=now,
        payload={"lang": "hi"},
        sequence_number=0,
    )
    appended0 = await audit_repo.append(ev0)
    assert appended0.prev_hash == GENESIS_HASH
    assert len(appended0.event_hash) == 64
    assert appended0.event_hash != ""

    # 2. Append second event
    ev1 = AuditEvent(
        event_id=uuid.uuid4(),
        session_id=sid,
        event_type=AuditEventType.CONSENT_GRANTED,
        timestamp=datetime(2026, 10, 18, 14, 1, 0, tzinfo=UTC),
        payload={"form": "dpdp_v1"},
        sequence_number=1,
    )
    appended1 = await audit_repo.append(ev1)
    assert appended1.prev_hash == appended0.event_hash
    assert len(appended1.event_hash) == 64

    # 3. Append third event: STANDING_ORDERS_ISSUED
    ev2 = AuditEvent(
        event_id=uuid.uuid4(),
        session_id=sid,
        event_type=AuditEventType.STANDING_ORDERS_ISSUED,
        timestamp=datetime(2026, 10, 18, 14, 2, 0, tzinfo=UTC),
        payload={"orders_count": 2},
        sequence_number=2,
    )
    appended2 = await audit_repo.append(ev2)
    assert appended2.prev_hash == appended1.event_hash
    assert len(appended2.event_hash) == 64

    # 4. Append fourth event: RESOURCE_ALLOCATED
    ev3 = AuditEvent(
        event_id=uuid.uuid4(),
        session_id=sid,
        event_type=AuditEventType.RESOURCE_ALLOCATED,
        timestamp=datetime(2026, 10, 18, 14, 3, 0, tzinfo=UTC),
        payload={"resource": "RESUS-BAY-01"},
        sequence_number=3,
    )
    appended3 = await audit_repo.append(ev3)
    assert appended3.prev_hash == appended2.event_hash

    # 5. Fetch all events from database and verify cryptographic chain
    events = await audit_repo.list_for_session(sid)
    assert len(events) == 4
    chain_result = verify_audit_chain(events)
    assert chain_result.is_valid is True
    assert chain_result.checked_events == 4
    assert chain_result.head_hash == appended3.event_hash
    assert chain_result.broken_at_seq is None
