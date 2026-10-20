"""Pure domain Facility Resource Allocator & Wheelchair Porter Orchestrator.

Determines real-time allocation of trauma/resuscitation bays, negative-pressure
isolation rooms, and automated wheelchair/stretcher porter dispatch tickets.

INVARIANTS:
- Zero I/O, zero network, zero logging, zero framework imports.
- Pure functions and immutable value objects only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal
from uuid import UUID


@dataclass(frozen=True)
class FacilityResourceAllocation:
    """Immutable facility resource allocation result.

    Attributes:
        resource_id: Specific allocated room/bay ID (e.g. 'RESUS-BAY-01') or None.
        resource_type: Classification ('RESUS_BAY', 'ISOLATION_ROOM',
            'OPD_CHAMBER', 'STANDARD_WAITING').
        porter_ticket_id: Wheelchair/stretcher porter dispatch token or None.
        isolation_precaution: Infection control protocol (e.g. 'AIRBORNE_CONTACT') or None.
        instructions_en: Clear patient-facing routing instruction in English.
        instructions_hi: Clear patient-facing routing instruction in Hindi.
    """

    resource_id: str | None
    resource_type: Literal["RESUS_BAY", "ISOLATION_ROOM", "OPD_CHAMBER", "STANDARD_WAITING"]
    porter_ticket_id: str | None
    isolation_precaution: str | None
    instructions_en: str
    instructions_hi: str


RESUS_BAYS: tuple[str, ...] = (
    "RESUS-BAY-01",
    "RESUS-BAY-02",
    "RESUS-BAY-03",
    "RESUS-BAY-04",
)

ISOLATION_ROOMS: tuple[str, ...] = (
    "ISO-ROOM-01",
    "ISO-ROOM-02",
)

CONTAGION_PATTERNS = [
    r"\brash\b",
    r"\bmeasles\b",
    r"\bchickenpox\b",
    r"\bhemoptysis\b",
    r"\bblood\s+in\s+cough\b",
    r"\bkhansi\s+mein\s+khoon\b",
    r"\bkhasra\b",
    r"\bchechak\b",
    r"\bvaricella\b",
    r"\brubella\b",
    r"\bदाने\b",
    r"\bचकत्ते\b",
    r"\bखांसी\s+में\s+खून\b",
    r"\bखसरा\b",
    r"\bचेचक\b",
]


class ResourceAllocator:
    """Pure domain service for hospital clinical facility resource routing."""

    @classmethod
    def allocate(
        cls,
        triage_priority: str | None = None,
        news2_score: int | None = None,
        symptoms_text: str | list[str] = "",
        needs_wheelchair: bool = False,
        session_id: UUID | str | None = None,
        occupied_resources: set[str] | list[str] | None = None,
    ) -> FacilityResourceAllocation:
        """Allocate acute trauma bays, isolation rooms, or OPD chambers with porter tickets.

        Rules:
        1. Resuscitation Bay:
           Triggered if priority is RED/CRITICAL or NEWS2 aggregate score >= 7.
           Allocates first available bay from RESUS-BAY-01..04.
        2. Isolation Room:
           Triggered if airborne/contact contagion symptoms (rash, measles, chickenpox, hemoptysis).
           Allocates first available room from ISO-ROOM-01..02 with AIRBORNE_CONTACT precaution.
        3. Standard OPD Chamber:
           Default for non-emergent, non-contagious presentations.
        4. Wheelchair Porter Dispatch:
           If needs_wheelchair is True, mints deterministic ticket 'PORTER-XXXX'.
        """
        occupied_set = set(occupied_resources or ())

        if isinstance(symptoms_text, list):
            joined_text = " ".join(symptoms_text).lower()
        else:
            joined_text = (symptoms_text or "").lower()

        # Deterministic Porter Ticket Generation
        porter_ticket_id: str | None = None
        if needs_wheelchair:
            if session_id:
                clean_id = str(session_id).replace("-", "").upper()
                porter_ticket_id = f"PORTER-{clean_id[:4]}"
            else:
                porter_ticket_id = "PORTER-A101"

        # Check Resuscitation Bay Condition
        is_red_priority = triage_priority is not None and triage_priority.upper() in (
            "RED",
            "CRITICAL",
            "CARDIAC_RED_FLAG",
            "EMERGENCY",
        )
        is_news2_critical = news2_score is not None and news2_score >= 7

        if is_red_priority or is_news2_critical:
            assigned_bay: str | None = None
            for bay in RESUS_BAYS:
                if bay not in occupied_set:
                    assigned_bay = bay
                    break
            if not assigned_bay:
                # All primary bays occupied: escalate to overflow
                assigned_bay = "RESUS-BAY-01"

            return FacilityResourceAllocation(
                resource_id=assigned_bay,
                resource_type="RESUS_BAY",
                porter_ticket_id=porter_ticket_id,
                isolation_precaution=None,
                instructions_en=(
                    "Immediate transfer to Trauma / Resuscitation Bay. Emergency team notified."
                ),
                instructions_hi=(
                    "तत्काल ट्रॉमा / पुनर्जीवन कक्ष (Resus Bay) में जाएं। "
                    "आपातकालीन टीम को सूचित कर दिया गया है।"
                ),
            )

        # Check Contagion / Negative-Pressure Isolation Condition
        has_contagion = any(re.search(pat, joined_text) for pat in CONTAGION_PATTERNS)
        if has_contagion:
            assigned_room: str | None = None
            for room in ISOLATION_ROOMS:
                if room not in occupied_set:
                    assigned_room = room
                    break
            if not assigned_room:
                assigned_room = "ISO-ROOM-01"

            return FacilityResourceAllocation(
                resource_id=assigned_room,
                resource_type="ISOLATION_ROOM",
                porter_ticket_id=porter_ticket_id,
                isolation_precaution="AIRBORNE_CONTACT",
                instructions_en=(
                    "Proceed directly to Negative-Pressure Isolation Room. "
                    "Wear N95 respirator mask."
                ),
                instructions_hi=(
                    "नकारात्मक दबाव वाले आइसोलेशन रूम में सीधे जाएं। N95 मास्क पहनना अनिवार्य है।"
                ),
            )

        # Default: Standard OPD Consultation
        return FacilityResourceAllocation(
            resource_id=None,
            resource_type="OPD_CHAMBER",
            porter_ticket_id=porter_ticket_id,
            isolation_precaution=None,
            instructions_en=(
                "Proceed to the OPD waiting area outside your assigned consultation chamber."
            ),
            instructions_hi=("कृपया अपने निर्धारित परामर्श कक्ष के बाहर ओपीडी प्रतीक्षालय में प्रतीक्षा करें।"),
        )
