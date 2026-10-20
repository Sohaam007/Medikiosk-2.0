"""Unit tests for Cryptographic SHA-256 Merkle Hash-Chained Audit Ledger.

Zero I/O, zero network, zero logging. Pure deterministic unit testing.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from medikiosk.domain.audit_chain import (
    GENESIS_HASH,
    compute_event_hash,
    verify_audit_chain,
)
from medikiosk.domain.contracts import AuditEvent, AuditEventType


def test_genesis_hash_constant() -> None:
    assert GENESIS_HASH == "0" * 64
    assert len(GENESIS_HASH) == 64


def test_compute_event_hash_deterministic() -> None:
    sid = uuid.uuid4()
    now_iso = "2026-10-18T10:00:00+00:00"
    hash1 = compute_event_hash(
        prev_hash=GENESIS_HASH,
        session_id=sid,
        seq=0,
        event_type="session_created",
        timestamp_iso=now_iso,
        metadata_keys_sorted={"patient_language": "hi", "kiosk_id": "K01"},
    )
    hash2 = compute_event_hash(
        prev_hash=GENESIS_HASH,
        session_id=sid,
        seq=0,
        event_type="session_created",
        timestamp_iso=now_iso,
        metadata_keys_sorted={"patient_language": "hi", "kiosk_id": "K01"},
    )
    assert hash1 == hash2
    assert len(hash1) == 64


def test_compute_event_hash_key_ordering_insensitivity() -> None:
    sid = uuid.uuid4()
    now_iso = "2026-10-18T10:00:00+00:00"
    hash1 = compute_event_hash(
        prev_hash=GENESIS_HASH,
        session_id=sid,
        seq=1,
        event_type="button_tapped",
        timestamp_iso=now_iso,
        metadata_keys_sorted={"alpha": 1, "beta": 2, "gamma": 3},
    )
    hash2 = compute_event_hash(
        prev_hash=GENESIS_HASH,
        session_id=sid,
        seq=1,
        event_type="button_tapped",
        timestamp_iso=now_iso,
        metadata_keys_sorted={"gamma": 3, "alpha": 1, "beta": 2},
    )
    assert hash1 == hash2


def test_verify_audit_chain_empty_list() -> None:
    result = verify_audit_chain([])
    assert result.is_valid is True
    assert result.checked_events == 0
    assert result.genesis_hash == GENESIS_HASH
    assert result.head_hash == GENESIS_HASH
    assert result.broken_at_seq is None


def test_verify_audit_chain_single_valid_event() -> None:
    sid = uuid.uuid4()
    now = datetime(2026, 10, 18, 12, 0, 0, tzinfo=UTC)
    h0 = compute_event_hash(
        prev_hash=GENESIS_HASH,
        session_id=sid,
        seq=0,
        event_type=AuditEventType.SESSION_CREATED.value,
        timestamp_iso=now.isoformat(),
        metadata_keys_sorted={"lang": "en"},
    )
    ev = AuditEvent(
        event_id=uuid.uuid4(),
        session_id=sid,
        event_type=AuditEventType.SESSION_CREATED,
        timestamp=now,
        payload={"lang": "en"},
        sequence_number=0,
        prev_hash=GENESIS_HASH,
        event_hash=h0,
    )
    res = verify_audit_chain([ev])
    assert res.is_valid is True
    assert res.checked_events == 1
    assert res.head_hash == h0
    assert res.broken_at_seq is None


def test_verify_audit_chain_multi_event_valid_provenance() -> None:
    sid = uuid.uuid4()
    events: list[AuditEvent] = []
    prev_h = GENESIS_HASH

    event_types = [
        AuditEventType.SESSION_CREATED,
        AuditEventType.CONSENT_GRANTED,
        AuditEventType.VOICE_CAPTURED,
        AuditEventType.STANDING_ORDERS_ISSUED,
        AuditEventType.RESOURCE_ALLOCATED,
    ]

    for seq, et in enumerate(event_types):
        ts = datetime(2026, 10, 18, 12, seq, 0, tzinfo=UTC)
        payload = {"step": seq}
        h = compute_event_hash(
            prev_hash=prev_h,
            session_id=sid,
            seq=seq,
            event_type=et.value,
            timestamp_iso=ts.isoformat(),
            metadata_keys_sorted=payload,
        )
        ev = AuditEvent(
            event_id=uuid.uuid4(),
            session_id=sid,
            event_type=et,
            timestamp=ts,
            payload=payload,
            sequence_number=seq,
            prev_hash=prev_h,
            event_hash=h,
        )
        events.append(ev)
        prev_h = h

    res = verify_audit_chain(events)
    assert res.is_valid is True
    assert res.checked_events == 5
    assert res.head_hash == events[-1].event_hash
    assert res.broken_at_seq is None


def test_tampering_payload_detected_at_exact_seq() -> None:
    sid = uuid.uuid4()
    events: list[AuditEvent] = []
    prev_h = GENESIS_HASH

    for seq in range(5):
        ts = datetime(2026, 10, 18, 12, seq, 0, tzinfo=UTC)
        payload = {"seq": seq}
        h = compute_event_hash(
            prev_hash=prev_h,
            session_id=sid,
            seq=seq,
            event_type=AuditEventType.BUTTON_TAPPED.value,
            timestamp_iso=ts.isoformat(),
            metadata_keys_sorted=payload,
        )
        ev = AuditEvent(
            event_id=uuid.uuid4(),
            session_id=sid,
            event_type=AuditEventType.BUTTON_TAPPED,
            timestamp=ts,
            payload=payload,
            sequence_number=seq,
            prev_hash=prev_h,
            event_hash=h,
        )
        events.append(ev)
        prev_h = h

    # Tamper with payload of event at sequence_number = 2
    tampered_ev2 = AuditEvent(
        event_id=events[2].event_id,
        session_id=events[2].session_id,
        event_type=events[2].event_type,
        timestamp=events[2].timestamp,
        payload={"seq": 2, "tampered_field": "hacked"},
        sequence_number=2,
        prev_hash=events[2].prev_hash,
        event_hash=events[2].event_hash,
    )
    events[2] = tampered_ev2

    res = verify_audit_chain(events)
    assert res.is_valid is False
    assert res.broken_at_seq == 2
    assert res.checked_events == 2


def test_tampering_event_hash_detected_at_exact_seq() -> None:
    sid = uuid.uuid4()
    events: list[AuditEvent] = []
    prev_h = GENESIS_HASH

    for seq in range(4):
        ts = datetime(2026, 10, 18, 12, seq, 0, tzinfo=UTC)
        payload = {"seq": seq}
        h = compute_event_hash(
            prev_hash=prev_h,
            session_id=sid,
            seq=seq,
            event_type=AuditEventType.BUTTON_TAPPED.value,
            timestamp_iso=ts.isoformat(),
            metadata_keys_sorted=payload,
        )
        ev = AuditEvent(
            event_id=uuid.uuid4(),
            session_id=sid,
            event_type=AuditEventType.BUTTON_TAPPED,
            timestamp=ts,
            payload=payload,
            sequence_number=seq,
            prev_hash=prev_h,
            event_hash=h,
        )
        events.append(ev)
        prev_h = h

    # Maliciously modify event_hash at sequence_number = 3
    tampered_ev3 = AuditEvent(
        event_id=events[3].event_id,
        session_id=events[3].session_id,
        event_type=events[3].event_type,
        timestamp=events[3].timestamp,
        payload=events[3].payload,
        sequence_number=3,
        prev_hash=events[3].prev_hash,
        event_hash="f" * 64,
    )
    events[3] = tampered_ev3

    res = verify_audit_chain(events)
    assert res.is_valid is False
    assert res.broken_at_seq == 3


def test_tampering_prev_hash_link_break_detected() -> None:
    sid = uuid.uuid4()
    events: list[AuditEvent] = []
    prev_h = GENESIS_HASH

    for seq in range(4):
        ts = datetime(2026, 10, 18, 12, seq, 0, tzinfo=UTC)
        payload = {"seq": seq}
        h = compute_event_hash(
            prev_hash=prev_h,
            session_id=sid,
            seq=seq,
            event_type=AuditEventType.BUTTON_TAPPED.value,
            timestamp_iso=ts.isoformat(),
            metadata_keys_sorted=payload,
        )
        ev = AuditEvent(
            event_id=uuid.uuid4(),
            session_id=sid,
            event_type=AuditEventType.BUTTON_TAPPED,
            timestamp=ts,
            payload=payload,
            sequence_number=seq,
            prev_hash=prev_h,
            event_hash=h,
        )
        events.append(ev)
        prev_h = h

    # Sever linkage at sequence_number = 1
    tampered_ev1 = AuditEvent(
        event_id=events[1].event_id,
        session_id=events[1].session_id,
        event_type=events[1].event_type,
        timestamp=events[1].timestamp,
        payload=events[1].payload,
        sequence_number=1,
        prev_hash="1" * 64,  # doesn't match events[0].event_hash
        event_hash=events[1].event_hash,
    )
    events[1] = tampered_ev1

    res = verify_audit_chain(events)
    assert res.is_valid is False
    assert res.broken_at_seq == 1


def test_verify_audit_chain_handles_unsorted_events() -> None:
    sid = uuid.uuid4()
    events: list[AuditEvent] = []
    prev_h = GENESIS_HASH

    for seq in range(3):
        ts = datetime(2026, 10, 18, 12, seq, 0, tzinfo=UTC)
        payload = {"seq": seq}
        h = compute_event_hash(
            prev_hash=prev_h,
            session_id=sid,
            seq=seq,
            event_type=AuditEventType.QUESTION_GENERATED.value,
            timestamp_iso=ts.isoformat(),
            metadata_keys_sorted=payload,
        )
        ev = AuditEvent(
            event_id=uuid.uuid4(),
            session_id=sid,
            event_type=AuditEventType.QUESTION_GENERATED,
            timestamp=ts,
            payload=payload,
            sequence_number=seq,
            prev_hash=prev_h,
            event_hash=h,
        )
        events.append(ev)
        prev_h = h

    # Pass in reversed order
    reversed_events = list(reversed(events))
    res = verify_audit_chain(reversed_events)
    assert res.is_valid is True
    assert res.checked_events == 3
    assert res.head_hash == events[-1].event_hash
