"""Unit tests for Facility Resource Allocator & Wheelchair Porter Orchestrator.

Zero I/O, zero network, zero logging. Pure deterministic unit testing.
"""

from __future__ import annotations

from uuid import UUID

from medikiosk.domain.resource_allocator import ResourceAllocator


def test_critical_priority_allocates_resus_bay() -> None:
    res = ResourceAllocator.allocate(triage_priority="CRITICAL")
    assert res.resource_type == "RESUS_BAY"
    assert res.resource_id == "RESUS-BAY-01"
    assert res.isolation_precaution is None
    assert "Trauma / Resuscitation Bay" in res.instructions_en


def test_red_priority_allocates_resus_bay() -> None:
    res = ResourceAllocator.allocate(triage_priority="RED")
    assert res.resource_type == "RESUS_BAY"
    assert res.resource_id == "RESUS-BAY-01"


def test_news2_score_high_allocates_resus_bay() -> None:
    res = ResourceAllocator.allocate(news2_score=9)
    assert res.resource_type == "RESUS_BAY"
    assert res.resource_id == "RESUS-BAY-01"


def test_news2_score_boundary_7_allocates_resus_bay() -> None:
    res = ResourceAllocator.allocate(news2_score=7)
    assert res.resource_type == "RESUS_BAY"
    assert res.resource_id == "RESUS-BAY-01"


def test_news2_score_below_7_does_not_trigger_resus() -> None:
    res = ResourceAllocator.allocate(news2_score=6)
    assert res.resource_type == "OPD_CHAMBER"
    assert res.resource_id is None


def test_occupied_resus_bay_skips_to_next_available() -> None:
    res = ResourceAllocator.allocate(
        triage_priority="CRITICAL",
        occupied_resources={"RESUS-BAY-01", "RESUS-BAY-02"},
    )
    assert res.resource_type == "RESUS_BAY"
    assert res.resource_id == "RESUS-BAY-03"


def test_all_resus_bays_occupied_fallback() -> None:
    res = ResourceAllocator.allocate(
        triage_priority="CRITICAL",
        occupied_resources={"RESUS-BAY-01", "RESUS-BAY-02", "RESUS-BAY-03", "RESUS-BAY-04"},
    )
    assert res.resource_type == "RESUS_BAY"
    assert res.resource_id == "RESUS-BAY-01"


def test_contagion_rash_allocates_isolation_room() -> None:
    res = ResourceAllocator.allocate(symptoms_text="Severe skin rash and fever suspected measles")
    assert res.resource_type == "ISOLATION_ROOM"
    assert res.resource_id == "ISO-ROOM-01"
    assert res.isolation_precaution == "AIRBORNE_CONTACT"
    assert "Negative-Pressure Isolation Room" in res.instructions_en
    assert "N95" in res.instructions_en


def test_contagion_hindi_keywords() -> None:
    res = ResourceAllocator.allocate(symptoms_text="Khasra aur chechak ke lakshan hain")
    assert res.resource_type == "ISOLATION_ROOM"
    assert res.resource_id == "ISO-ROOM-01"
    assert res.isolation_precaution == "AIRBORNE_CONTACT"


def test_contagion_hemoptysis() -> None:
    res = ResourceAllocator.allocate(symptoms_text="Coughing with blood in cough and hemoptysis")
    assert res.resource_type == "ISOLATION_ROOM"
    assert res.resource_id == "ISO-ROOM-01"
    assert res.isolation_precaution == "AIRBORNE_CONTACT"


def test_occupied_isolation_room_skips_to_iso_02() -> None:
    res = ResourceAllocator.allocate(
        symptoms_text="chickenpox blisters",
        occupied_resources={"ISO-ROOM-01"},
    )
    assert res.resource_type == "ISOLATION_ROOM"
    assert res.resource_id == "ISO-ROOM-02"


def test_wheelchair_request_mints_deterministic_ticket() -> None:
    session_id = UUID("abcdef01-2345-6789-abcd-ef0123456789")
    res = ResourceAllocator.allocate(
        needs_wheelchair=True,
        session_id=session_id,
    )
    assert res.porter_ticket_id == "PORTER-ABCD"


def test_wheelchair_request_without_session_id() -> None:
    res = ResourceAllocator.allocate(needs_wheelchair=True, session_id=None)
    assert res.porter_ticket_id == "PORTER-A101"


def test_standard_presentation_allocates_opd_chamber() -> None:
    res = ResourceAllocator.allocate(
        triage_priority="ROUTINE",
        news2_score=1,
        symptoms_text="Mild knee pain for 2 weeks",
        needs_wheelchair=False,
    )
    assert res.resource_type == "OPD_CHAMBER"
    assert res.resource_id is None
    assert res.porter_ticket_id is None
    assert res.isolation_precaution is None
    assert "OPD waiting area" in res.instructions_en
