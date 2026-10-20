"""End-to-End tests for MediKiosk Phase X.3 Autonomous Clinical Intelligence.

Waves 19-23:
- Wave 19: POST /api/intake/standing-orders (cardiac, fever, metabolic, 410)
- Wave 20: POST /api/resources/allocate & GET /api/resources/status
- Wave 21: POST /api/clinician/verify-rx-safety & link-care-context firewall
- Wave 22: GET /api/audit/verify-chain/{session_id} (Merkle chain verification)
- Wave 23: POST /api/intake/caregiver-pass (E.164 phone validation, hashing)
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from medikiosk.domain.audit_chain import GENESIS_HASH, calculate_event_hash
from medikiosk.domain.contracts import (
    AuditEvent,
    AuditEventType,
    SessionStatus,
)
from tests.e2e.conftest import fake_audit_repo, fake_session_repo


@pytest.mark.e2e
def test_standing_orders_cardiac_emergency_ecg_and_troponin(client_kiosk: TestClient) -> None:
    """POST /api/intake/standing-orders with cardiac presentation routes ECG and Troponin."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "hi", "tenant_id": "test_tenant", "department_id": "emergency"},
    )
    assert start_resp.status_code == 201
    session_id = start_resp.json()["session_id"]

    order_payload = {
        "session_id": session_id,
        "symptoms_text": "Severe crushing chest pain radiating to left arm and jaw with sweating",
        "age": 55,
    }
    resp = client_kiosk.post("/api/intake/standing-orders", json=order_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["session_id"] == session_id
    order_codes = [o["code"] for o in data["orders"]]
    assert "ECG-01" in order_codes
    assert "LAB-TROP" in order_codes
    assert data["estimated_time_saved_minutes"] >= 45
    assert (
        "cardiac" in data["clinical_rationale"].lower()
        or "chest pain" in data["clinical_rationale"].lower()
    )

    # Verify orders were persisted on the session in the repository
    session = fake_session_repo._store[session_id]
    assert session.recommended_labs_json is not None
    saved_labs = json.loads(session.recommended_labs_json)
    saved_codes = [item["code"] for item in saved_labs]
    assert "ECG-01" in saved_codes
    assert "LAB-TROP" in saved_codes

    # Verify zero-PHI audit event appended
    events = [
        e
        for e in fake_audit_repo._events
        if str(e.session_id) == session_id and e.event_type == AuditEventType.STANDING_ORDERS_ISSUED
    ]
    assert len(events) >= 1
    audit_payload = events[-1].payload
    assert audit_payload["order_count"] == len(data["orders"])
    assert "ECG-01" in audit_payload["order_codes"]
    assert "crushing chest pain" not in str(audit_payload)


@pytest.mark.e2e
def test_standing_orders_acute_fever_cbc_dengue_malaria(client_kiosk: TestClient) -> None:
    """POST /api/intake/standing-orders with fever triggers CBC, Dengue, and Malaria orders."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "en", "tenant_id": "test_tenant", "department_id": "general"},
    )
    session_id = start_resp.json()["session_id"]

    order_payload = {
        "session_id": session_id,
        "symptoms_text": "High grade fever with chills, body ache and suspected dengue",
        "age": 28,
    }
    resp = client_kiosk.post("/api/intake/standing-orders", json=order_payload)
    assert resp.status_code == 200
    data = resp.json()

    order_codes = [o["code"] for o in data["orders"]]
    assert "LAB-CBC" in order_codes
    assert "LAB-DENGUE" in order_codes
    assert "LAB-MP" in order_codes
    assert data["estimated_time_saved_minutes"] >= 60


@pytest.mark.e2e
def test_standing_orders_routine_metabolic_screening_for_age_ge_45(
    client_kiosk: TestClient,
) -> None:
    """POST /api/intake/standing-orders for routine presentation with age >= 45 recommends CBG."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "en", "tenant_id": "test_tenant", "department_id": "general"},
    )
    session_id = start_resp.json()["session_id"]

    order_payload = {
        "session_id": session_id,
        "symptoms_text": "Mild headache and routine checkup",
        "age": 50,
    }
    resp = client_kiosk.post("/api/intake/standing-orders", json=order_payload)
    assert resp.status_code == 200
    data = resp.json()

    order_codes = [o["code"] for o in data["orders"]]
    assert "LAB-CBG" in order_codes
    assert data["estimated_time_saved_minutes"] >= 15


@pytest.mark.e2e
def test_standing_orders_respiratory_distress_cxr_and_abg(client_kiosk: TestClient) -> None:
    """POST /api/intake/standing-orders with severe breathlessness routes Chest X-Ray and ABG."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "en", "tenant_id": "test_tenant", "department_id": "pulmonology"},
    )
    session_id = start_resp.json()["session_id"]

    order_payload = {
        "session_id": session_id,
        "symptoms_text": "Severe breathlessness, wheezing, and acute respiratory distress",
        "age": 35,
    }
    resp = client_kiosk.post("/api/intake/standing-orders", json=order_payload)
    assert resp.status_code == 200
    data = resp.json()

    order_codes = [o["code"] for o in data["orders"]]
    assert "RAD-CXR" in order_codes
    assert "LAB-ABG" in order_codes
    assert data["estimated_time_saved_minutes"] >= 40


@pytest.mark.e2e
def test_standing_orders_terminated_session_returns_410(client_kiosk: TestClient) -> None:
    """POST /api/intake/standing-orders returns 410 Gone for terminated or purged session."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "en", "tenant_id": "test_tenant", "department_id": "general"},
    )
    session_id = start_resp.json()["session_id"]

    # Terminate the session
    session = fake_session_repo._store[session_id]
    fake_session_repo._store[session_id] = session.model_copy(
        update={"status": SessionStatus.TERMINATED}
    )

    resp = client_kiosk.post(
        "/api/intake/standing-orders",
        json={"session_id": session_id, "symptoms_text": "Chest pain", "age": 40},
    )
    assert resp.status_code == 410


@pytest.mark.e2e
def test_allocate_resource_priority_red_resus_bay(client_kiosk: TestClient) -> None:
    """POST /api/resources/allocate with RED priority routes to RESUS-BAY-01."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "en", "tenant_id": "test_tenant", "department_id": "emergency"},
    )
    session_id = start_resp.json()["session_id"]

    alloc_payload = {
        "session_id": session_id,
        "symptoms_text": "Severe trauma with unresponsive patient",
        "triage_priority": "RED",
        "news2_score": 8,
        "needs_wheelchair": False,
    }
    resp = client_kiosk.post("/api/resources/allocate", json=alloc_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["session_id"] == session_id
    assert data["resource_id"] == "RESUS-BAY-01"
    assert data["resource_type"] == "RESUS_BAY"
    assert data["isolation_precaution"] is None
    assert "Trauma / Resuscitation Bay" in data["instructions_en"]
    assert "पुनर्जीवन कक्ष" in data["instructions_hi"]

    # Verify session model updated
    session = fake_session_repo._store[session_id]
    assert session.allocated_resource_id == "RESUS-BAY-01"

    # Verify audit event recorded without PHI
    events = [
        e
        for e in fake_audit_repo._events
        if str(e.session_id) == session_id and e.event_type == AuditEventType.RESOURCE_ALLOCATED
    ]
    assert len(events) >= 1
    assert events[-1].payload["resource_id"] == "RESUS-BAY-01"
    assert events[-1].payload["resource_type"] == "RESUS_BAY"


@pytest.mark.e2e
def test_allocate_resource_contagion_isolation_room(client_kiosk: TestClient) -> None:
    """POST /api/resources/allocate with rash and measles routes to Negative-Pressure Isolation."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "hi", "tenant_id": "test_tenant", "department_id": "general"},
    )
    session_id = start_resp.json()["session_id"]

    alloc_payload = {
        "session_id": session_id,
        "symptoms_text": "Fever with severe skin rash and chickenpox blisters",
        "triage_priority": "URGENT",
        "news2_score": 2,
        "needs_wheelchair": False,
    }
    resp = client_kiosk.post("/api/resources/allocate", json=alloc_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["resource_id"] == "ISO-ROOM-01"
    assert data["resource_type"] == "ISOLATION_ROOM"
    assert data["isolation_precaution"] == "AIRBORNE_CONTACT"
    assert "N95" in data["instructions_en"]
    assert "आइसोलेशन रूम" in data["instructions_hi"]


@pytest.mark.e2e
def test_allocate_resource_wheelchair_porter_dispatch(client_kiosk: TestClient) -> None:
    """POST /api/resources/allocate with needs_wheelchair mints deterministic PORTER ticket."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "en", "tenant_id": "test_tenant", "department_id": "general"},
    )
    session_id = start_resp.json()["session_id"]

    alloc_payload = {
        "session_id": session_id,
        "symptoms_text": "Elderly patient unable to walk, joint pain",
        "needs_wheelchair": True,
    }
    resp = client_kiosk.post("/api/resources/allocate", json=alloc_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["porter_ticket_id"] is not None
    assert re.match(r"^PORTER-[A-Z0-9]{4}$", data["porter_ticket_id"])

    # Verify session updated with porter ticket
    session = fake_session_repo._store[session_id]
    assert session.porter_ticket_id == data["porter_ticket_id"]


@pytest.mark.e2e
def test_allocate_resource_sequential_occupancy(client_kiosk: TestClient) -> None:
    """POST /api/resources/allocate assigns available bays sequentially when multiple arrive."""
    # Session 1
    s1 = client_kiosk.post("/api/intake/start", json={"patient_language": "en"}).json()[
        "session_id"
    ]
    r1 = client_kiosk.post(
        "/api/resources/allocate",
        json={"session_id": s1, "triage_priority": "RED"},
    )
    assert r1.status_code == 200
    bay1 = r1.json()["resource_id"]
    assert bay1 in ("RESUS-BAY-01", "RESUS-BAY-02", "RESUS-BAY-03", "RESUS-BAY-04")
    assert r1.json()["resource_type"] == "RESUS_BAY"

    # Session 2 arrives while Session 1 occupies bay1
    s2 = client_kiosk.post("/api/intake/start", json={"patient_language": "en"}).json()[
        "session_id"
    ]
    r2 = client_kiosk.post(
        "/api/resources/allocate",
        json={"session_id": s2, "triage_priority": "RED"},
    )
    assert r2.status_code == 200
    bay2 = r2.json()["resource_id"]
    assert bay2 in ("RESUS-BAY-01", "RESUS-BAY-02", "RESUS-BAY-03", "RESUS-BAY-04")
    assert bay2 != bay1
    assert r2.json()["resource_type"] == "RESUS_BAY"


@pytest.mark.e2e
def test_allocate_resource_terminated_session_returns_410(client_kiosk: TestClient) -> None:
    """POST /api/resources/allocate returns 410 Gone if session is terminated."""
    start_resp = client_kiosk.post("/api/intake/start", json={"patient_language": "en"})
    session_id = start_resp.json()["session_id"]

    session = fake_session_repo._store[session_id]
    fake_session_repo._store[session_id] = session.model_copy(
        update={"status": SessionStatus.TERMINATED}
    )

    resp = client_kiosk.post(
        "/api/resources/allocate",
        json={"session_id": session_id, "triage_priority": "RED"},
    )
    assert resp.status_code == 410


@pytest.mark.e2e
def test_get_resources_status_grid(client_kiosk: TestClient) -> None:
    """GET /api/resources/status returns occupancy grid across bays, rooms, and porters."""
    resp = client_kiosk.get("/api/resources/status")
    assert resp.status_code == 200
    data = resp.json()

    assert "resus_bays" in data
    assert len(data["resus_bays"]) == 4
    bay_ids = [b["bay_id"] for b in data["resus_bays"]]
    assert bay_ids == ["RESUS-BAY-01", "RESUS-BAY-02", "RESUS-BAY-03", "RESUS-BAY-04"]

    assert "isolation_rooms" in data
    assert len(data["isolation_rooms"]) == 2
    room_ids = [r["room_id"] for r in data["isolation_rooms"]]
    assert room_ids == ["ISO-ROOM-01", "ISO-ROOM-02"]

    assert "active_porters" in data
    assert "total_resus_occupied" in data
    assert "total_isolation_occupied" in data
    assert "total_active_porters" in data


@pytest.mark.e2e
def test_verify_rx_safety_critical_contraindication_anticoagulant_nsaid(
    client_kiosk: TestClient,
) -> None:
    """POST /api/clinician/verify-rx-safety flags Warfarin + Aspirin as contraindicated."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "en", "tenant_id": "test_tenant", "department_id": "cardiology"},
    )
    session_id = start_resp.json()["session_id"]

    rx_payload = {
        "session_id": session_id,
        "prescribed_medications": ["Aspirin 150mg OD"],
        "existing_medications": ["Warfarin 5mg OD"],
        "allergies": [],
    }
    resp = client_kiosk.post("/api/clinician/verify-rx-safety", json=rx_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["session_id"] == session_id
    assert data["is_safe"] is False
    assert data["severity"] == "CRITICAL_CONTRAINDICATION"
    assert data["requires_override"] is True
    assert len(data["alerts"]) >= 1

    rule_ids = [a["rule_id"] for a in data["alerts"]]
    assert "RULE-DDI-001" in rule_ids
    assert "CRITICAL CONTRAINDICATION DETECTED" in data["message"]


@pytest.mark.e2e
def test_verify_rx_safety_clean_prescription_is_safe(client_kiosk: TestClient) -> None:
    """POST /api/clinician/verify-rx-safety clears standard non-interacting medications."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "en", "tenant_id": "test_tenant", "department_id": "general"},
    )
    session_id = start_resp.json()["session_id"]

    rx_payload = {
        "session_id": session_id,
        "prescribed_medications": ["Paracetamol 650mg TDS", "Amoxicillin 500mg BD"],
        "existing_medications": ["Multivitamins"],
        "allergies": [],
    }
    resp = client_kiosk.post("/api/clinician/verify-rx-safety", json=rx_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["is_safe"] is True
    assert data["severity"] == "SAFE"
    assert data["requires_override"] is False
    assert len(data["alerts"]) == 0


@pytest.mark.e2e
def test_verify_rx_safety_beta_blocker_bradycardia_contraindication(
    client_kiosk: TestClient,
) -> None:
    """POST /api/clinician/verify-rx-safety flags Beta-Blocker when pulse < 55 bpm."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "en", "tenant_id": "test_tenant", "department_id": "general"},
    )
    session_id = start_resp.json()["session_id"]

    # Record bradycardic vitals (pulse 48 bpm)
    client_kiosk.post(
        "/api/intake/vitals",
        json={
            "session_id": session_id,
            "spo2_percent": 98,
            "systolic_bp_mmhg": 118,
            "diastolic_bp_mmhg": 76,
            "pulse_bpm": 48,
            "temperature_c": 36.6,
            "respiration_rate": 14,
        },
    )

    rx_payload = {
        "session_id": session_id,
        "prescribed_medications": ["Metoprolol 50mg BD"],
        "existing_medications": [],
        "allergies": [],
    }
    resp = client_kiosk.post("/api/clinician/verify-rx-safety", json=rx_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["is_safe"] is False
    assert data["severity"] == "CRITICAL_CONTRAINDICATION"
    assert data["requires_override"] is True
    rule_ids = [a["rule_id"] for a in data["alerts"]]
    assert "RULE-VIT-004" in rule_ids


@pytest.mark.e2e
def test_verify_rx_safety_allergy_cross_matching(client_kiosk: TestClient) -> None:
    """POST /api/clinician/verify-rx-safety alerts when Penicillin allergic gets Amoxicillin."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "en", "tenant_id": "test_tenant", "department_id": "general"},
    )
    session_id = start_resp.json()["session_id"]

    rx_payload = {
        "session_id": session_id,
        "prescribed_medications": ["Amoxicillin 500mg TDS"],
        "existing_medications": [],
        "allergies": ["Penicillin anaphylaxis"],
    }
    resp = client_kiosk.post("/api/clinician/verify-rx-safety", json=rx_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["is_safe"] is False
    rule_ids = [a["rule_id"] for a in data["alerts"]]
    assert "RULE-ALG-006" in rule_ids


@pytest.mark.e2e
def test_link_care_context_blocked_on_critical_contraindication_without_override(
    client_kiosk: TestClient,
) -> None:
    """POST /api/abdm/link-care-context returns 422 when DDI lacks clinician override."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "en", "tenant_id": "test_tenant", "department_id": "general"},
    )
    session_id = start_resp.json()["session_id"]

    # Warfarin + Aspirin -> CRITICAL_CONTRAINDICATION
    req_payload = {
        "session_id": session_id,
        "abha_id": "91-1234-5678-9012",
        "soap_note": "Cardiac review with high bleeding risk combo.",
        "prescribed_medications": ["Warfarin 5mg", "Aspirin 75mg"],
        "clinician_override_reason": None,
    }

    resp = client_kiosk.post("/api/abdm/link-care-context", json=req_payload)
    assert resp.status_code == 422
    assert "CRITICAL_CONTRAINDICATION" in resp.json()["detail"]


@pytest.mark.e2e
def test_link_care_context_passes_with_clinician_override_reason(
    client_kiosk: TestClient,
) -> None:
    """POST /api/abdm/link-care-context succeeds with valid clinician override reason on DDI."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "en", "tenant_id": "test_tenant", "department_id": "general"},
    )
    session_id = start_resp.json()["session_id"]

    override_text = "Cardiologist approved dual therapy for mechanical valve post-PCI"
    req_payload = {
        "session_id": session_id,
        "abha_id": "91-1234-5678-9012",
        "soap_note": "Cardiac review with approved dual therapy.",
        "prescribed_medications": ["Warfarin 5mg", "Aspirin 75mg"],
        "clinician_override_reason": override_text,
    }

    resp = client_kiosk.post("/api/abdm/link-care-context", json=req_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["session_id"] == session_id
    assert data["status"] == "LINKED"
    assert re.match(r"^RX-[0-9A-F]{4}$", data["pharmacy_token"])

    # Verify override was recorded in the audit event with zero-PHI
    events = [
        e
        for e in fake_audit_repo._events
        if str(e.session_id) == session_id and e.event_type == AuditEventType.CARE_CONTEXT_LINKED
    ]
    assert len(events) >= 1
    audit_payload = events[-1].payload
    assert audit_payload.get("override_applied") is True
    assert "override_reason_hash" in audit_payload
    # Raw override text must NOT be present
    assert override_text not in str(audit_payload)


@pytest.mark.e2e
def test_caregiver_pass_minting_and_e164_validation(client_kiosk: TestClient) -> None:
    """POST /api/intake/caregiver-pass mints CG-XXXX pass and enforces zero-PHI phone hashing."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "hi", "tenant_id": "test_tenant", "department_id": "general"},
    )
    session_id = start_resp.json()["session_id"]

    pass_payload = {
        "session_id": session_id,
        "caregiver_phone": "+919876543210",
    }
    resp = client_kiosk.post("/api/intake/caregiver-pass", json=pass_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["session_id"] == session_id
    assert re.match(r"^CG-[0-9A-F]{4}$", data["caregiver_pass_id"])
    assert "issued_at" in data

    # Verify zero-PHI phone hashing in audit trail
    events = [
        e
        for e in fake_audit_repo._events
        if str(e.session_id) == session_id and e.event_type == AuditEventType.CAREGIVER_PASS_ISSUED
    ]
    assert len(events) >= 1
    event_payload = events[-1].payload
    assert "caregiver_phone_hash" in event_payload
    assert event_payload["caregiver_pass_id"] == data["caregiver_pass_id"]
    # Phone number must never appear in raw format
    assert "+919876543210" not in str(event_payload)
    assert "9876543210" not in str(event_payload)


@pytest.mark.e2e
def test_caregiver_pass_invalid_phone_rejected(client_kiosk: TestClient) -> None:
    """POST /api/intake/caregiver-pass rejects invalid non-E.164 phone formats with 422."""
    session_id = str(uuid4())
    resp = client_kiosk.post(
        "/api/intake/caregiver-pass",
        json={"session_id": session_id, "caregiver_phone": "abc-invalid-123"},
    )
    assert resp.status_code == 422


@pytest.mark.e2e
def test_audit_verify_chain_nonexistent_session_returns_404(client_kiosk: TestClient) -> None:
    """GET /api/audit/verify-chain/{session_id} returns 404 for unknown session UUID."""
    unknown_sid = str(uuid4())
    resp = client_kiosk.get(f"/api/audit/verify-chain/{unknown_sid}")
    assert resp.status_code == 404


@pytest.mark.e2e
def test_audit_verify_chain_intact_and_tamper_detection(client_kiosk: TestClient) -> None:
    """GET /api/audit/verify-chain validates valid Merkle chain and detects tampering."""
    start_resp = client_kiosk.post(
        "/api/intake/start",
        json={"patient_language": "en", "tenant_id": "test_tenant", "department_id": "general"},
    )
    session_id_str = start_resp.json()["session_id"]
    sid = UUID(session_id_str)
    now = datetime.now(UTC)

    # Clear existing events for this session in fake_audit_repo and construct 3-event chain
    fake_audit_repo._events = [
        e for e in fake_audit_repo._events if str(e.session_id) != session_id_str
    ]

    # Event 0: Genesis link
    ts0 = now.isoformat()
    h0 = calculate_event_hash(
        prev_hash=GENESIS_HASH,
        session_id=sid,
        seq=0,
        event_type=AuditEventType.SESSION_CREATED.value,
        timestamp_iso=ts0,
        metadata_keys_sorted={"lang": "en"},
    )
    ev0 = AuditEvent(
        event_id=uuid4(),
        session_id=sid,
        event_type=AuditEventType.SESSION_CREATED,
        timestamp=now,
        sequence_number=0,
        prev_hash=GENESIS_HASH,
        event_hash=h0,
        payload={"lang": "en"},
    )

    # Event 1: Linked to ev0
    h1 = calculate_event_hash(
        prev_hash=h0,
        session_id=sid,
        seq=1,
        event_type=AuditEventType.CONSENT_GRANTED.value,
        timestamp_iso=ts0,
        metadata_keys_sorted={"consent": True},
    )
    ev1 = AuditEvent(
        event_id=uuid4(),
        session_id=sid,
        event_type=AuditEventType.CONSENT_GRANTED,
        timestamp=now,
        sequence_number=1,
        prev_hash=h0,
        event_hash=h1,
        payload={"consent": True},
    )

    # Event 2: Linked to ev1
    h2 = calculate_event_hash(
        prev_hash=h1,
        session_id=sid,
        seq=2,
        event_type=AuditEventType.RESOURCE_ALLOCATED.value,
        timestamp_iso=ts0,
        metadata_keys_sorted={"resource_id": "RESUS-BAY-01"},
    )
    ev2 = AuditEvent(
        event_id=uuid4(),
        session_id=sid,
        event_type=AuditEventType.RESOURCE_ALLOCATED,
        timestamp=now,
        sequence_number=2,
        prev_hash=h1,
        event_hash=h2,
        payload={"resource_id": "RESUS-BAY-01"},
    )

    fake_audit_repo._events.extend([ev0, ev1, ev2])

    # 1. Verify valid unbroken chain
    resp_valid = client_kiosk.get(f"/api/audit/verify-chain/{sid}")
    assert resp_valid.status_code == 200
    data_valid = resp_valid.json()
    assert data_valid["is_valid"] is True
    assert data_valid["checked_events"] == 3
    assert data_valid["genesis_hash"] == GENESIS_HASH
    assert data_valid["head_hash"] == h2
    assert data_valid["broken_at_seq"] is None
    assert "verified successfully" in data_valid["message"]

    # 2. Introduce artificial tampering in event 1 payload (e.g. malicious alteration)
    tampered_ev1 = AuditEvent(
        event_id=ev1.event_id,
        session_id=sid,
        event_type=AuditEventType.CONSENT_GRANTED,
        timestamp=now,
        sequence_number=1,
        prev_hash=h0,
        event_hash=h1,
        payload={"consent": False},  # Tampered payload!
    )
    fake_audit_repo._events = [ev0, tampered_ev1, ev2]

    resp_tampered = client_kiosk.get(f"/api/audit/verify-chain/{sid}")
    assert resp_tampered.status_code == 200
    data_tampered = resp_tampered.json()
    assert data_tampered["is_valid"] is False
    assert data_tampered["checked_events"] == 1
    assert data_tampered["broken_at_seq"] == 1
    assert "broken at sequence 1" in data_tampered["message"]
