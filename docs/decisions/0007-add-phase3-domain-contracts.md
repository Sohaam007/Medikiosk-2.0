# ADR 0007: Add Phase 3 Clinical Standing Orders, Facility Resources, and Cryptographic Audit Ledger Contracts

## Context
Phase X.3 (Waves 19–22) introduces Autonomous Clinical Intelligence and Medico-Legal Fortress capabilities:
1. Wave 19: Clinical Standing Orders (CSO) & Pre-Consultation Lab Router recommendation persistence.
2. Wave 20: Real-time Trauma/Resuscitation Bay, Negative-Pressure Isolation Room, and Wheelchair Porter ticket allocation.
3. Wave 22: Cryptographic SHA-256 Merkle Hash-Chained Audit Ledger for tamper-evident event chains.
4. Wave 23: Caregiver companion pass issuance.

To support persistence and verification without violating Clean Architecture invariants or breaking backward compatibility, domain contracts and database models must be widened.

## Decision
1. Widen `SessionState` (`src/medikiosk/domain/contracts/session.py`) by adding three optional fields:
   - `recommended_labs_json: str | None = None`: Serialized JSON array of pre-consultation lab/imaging orders.
   - `allocated_resource_id: str | None = None`: Identifier of the allocated clinical room/bay (e.g. `RESUS-BAY-01`, `ISO-ROOM-01`).
   - `porter_ticket_id: str | None = None`: Assigned wheelchair porter dispatch token (e.g. `PORTER-XXXX`).

2. Widen `AuditEvent` (`src/medikiosk/domain/contracts/audit.py`) with cryptographic hash-chain fields:
   - `prev_hash: str = Field(default="0" * 64, min_length=64, max_length=64)`: SHA-256 hash of the preceding event in the session, or genesis hash (`"0" * 64`) for sequence 0.
   - `event_hash: str = Field(default="", max_length=64)`: Canonical SHA-256 digest of the current audit event.

3. Expand `AuditEventType` (`src/medikiosk/domain/contracts/audit.py`) with:
   - `STANDING_ORDERS_ISSUED = "standing_orders_issued"`
   - `RESOURCE_ALLOCATED = "resource_allocated"`
   - `CAREGIVER_PASS_ISSUED = "caregiver_pass_issued"`

4. Update `SessionModel` and `AuditEventModel` in `src/medikiosk/adapters/database/models.py` with corresponding columns.

5. Update `SQLSessionRepository` to round-trip the new session fields.

6. Update `SQLAuditRepository.append` to automatically compute and link cryptographic event hashes from the latest stored sequence or genesis hash when `event_hash` is unpopulated.

## Consequences
- Full backward compatibility is preserved: all new session attributes default to `None`, and audit fields default to standard genesis / blank values.
- Enables tamper-evident verification of audit events at exact sequence indices.
- Preserves Clean Architecture boundaries and zero-PHI guarantees across all layers.
