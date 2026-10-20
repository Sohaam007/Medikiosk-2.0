"""Pure domain Cryptographic SHA-256 Merkle Hash-Chained Audit Ledger.

Enforces cryptographic immutability, tamper evidence, and unbroken provenance
across all medico-legal intake interactions from GENESIS_HASH to head_hash.

INVARIANTS:
- Zero I/O, zero network, zero logging, zero external framework imports.
- Pure functions and immutable value objects only.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any
from uuid import UUID

GENESIS_HASH: str = "0" * 64


def calculate_event_hash(
    prev_hash: str,
    session_id: str | UUID,
    seq: int,
    event_type: str,
    timestamp_iso: str,
    metadata_keys_sorted: dict[str, Any] | None = None,
) -> str:
    """Compute deterministic SHA-256 cryptographic digest linking an event to prev_hash.

    Format:
    sha256("{prev_hash}:{session_id}:{seq}:{event_type}:{timestamp_iso}:{sorted_payload_json}")
    """
    sorted_json = json.dumps(metadata_keys_sorted or {}, sort_keys=True, separators=(",", ":"))
    raw = f"{prev_hash}:{session_id!s}:{seq}:{event_type}:{timestamp_iso}:{sorted_json}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


compute_event_hash = calculate_event_hash


@dataclass(frozen=True)
class AuditChainVerificationResult:
    """Immutable result of cryptographic hash chain verification.

    Attributes:
        is_valid: True if every hash matches and previous hash linkages are intact.
        checked_events: Number of audit events verified before completion or failure.
        genesis_hash: The root parent hash of the verified session ledger.
        head_hash: The most recent event hash verified, or GENESIS_HASH if empty.
        broken_at_seq: Sequence number where chain tampering was detected, or None if valid.
    """

    is_valid: bool
    checked_events: int
    genesis_hash: str
    head_hash: str
    broken_at_seq: int | None


def verify_audit_chain(events: Sequence[Any]) -> AuditChainVerificationResult:
    """Verify cryptographic chain continuity and integrity for an ordered AuditEvent sequence."""
    if not events:
        return AuditChainVerificationResult(
            is_valid=True,
            checked_events=0,
            genesis_hash=GENESIS_HASH,
            head_hash=GENESIS_HASH,
            broken_at_seq=None,
        )

    # Sort events by sequence_number monotonically
    sorted_events = sorted(events, key=lambda e: getattr(e, "sequence_number", 0))

    for i, ev in enumerate(sorted_events):
        expected_prev = GENESIS_HASH if i == 0 else sorted_events[i - 1].event_hash
        ev_prev = getattr(ev, "prev_hash", "")
        ev_seq = getattr(ev, "sequence_number", 0)

        # Check hash linkage to previous record
        if ev_prev != expected_prev:
            return AuditChainVerificationResult(
                is_valid=False,
                checked_events=i,
                genesis_hash=getattr(sorted_events[0], "prev_hash", GENESIS_HASH),
                head_hash=getattr(sorted_events[i - 1], "event_hash", GENESIS_HASH)
                if i > 0
                else GENESIS_HASH,
                broken_at_seq=ev_seq,
            )

        # Re-compute digest and compare
        ev_type = getattr(ev, "event_type", "")
        ev_type_str = ev_type.value if hasattr(ev_type, "value") else str(ev_type)
        ev_ts = getattr(ev, "timestamp", "")
        ts_iso = ev_ts.isoformat() if hasattr(ev_ts, "isoformat") else str(ev_ts)
        ev_payload = getattr(ev, "payload", {})

        computed_hash = compute_event_hash(
            prev_hash=ev_prev,
            session_id=getattr(ev, "session_id", ""),
            seq=ev_seq,
            event_type=ev_type_str,
            timestamp_iso=ts_iso,
            metadata_keys_sorted=ev_payload if isinstance(ev_payload, dict) else {},
        )

        ev_hash = getattr(ev, "event_hash", "")
        if ev_hash != computed_hash:
            return AuditChainVerificationResult(
                is_valid=False,
                checked_events=i,
                genesis_hash=getattr(sorted_events[0], "prev_hash", GENESIS_HASH),
                head_hash=getattr(sorted_events[i - 1], "event_hash", GENESIS_HASH)
                if i > 0
                else GENESIS_HASH,
                broken_at_seq=ev_seq,
            )

    return AuditChainVerificationResult(
        is_valid=True,
        checked_events=len(sorted_events),
        genesis_hash=getattr(sorted_events[0], "prev_hash", GENESIS_HASH),
        head_hash=getattr(sorted_events[-1], "event_hash", GENESIS_HASH),
        broken_at_seq=None,
    )
