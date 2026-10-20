"""Pydantic schemas for the Facility Resources & Porter Orchestrator endpoints.

Covers:
- POST /api/resources/allocate
- GET /api/resources/status

SECURITY: Zero PHI. Only session IDs, resource codes, and operational flags are exposed.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class AllocateResourceRequest(BaseModel):
    """Request body for POST /api/resources/allocate."""

    session_id: UUID = Field(..., description="Active patient session UUID")
    symptoms_text: str = Field(default="", description="Presenting symptoms text. PHI - never log.")
    triage_priority: str | None = Field(
        default=None, description="Optional triage priority e.g. RED, CRITICAL"
    )
    news2_score: int | None = Field(
        default=None, ge=0, le=20, description="Optional aggregate NEWS2 score (0-20)"
    )
    needs_wheelchair: bool = Field(
        default=False, description="Whether patient requires wheelchair assistance"
    )


class AllocateResourceResponse(BaseModel):
    """Response body for POST /api/resources/allocate."""

    session_id: UUID
    resource_id: str | None = Field(
        default=None, description="Allocated room or bay (e.g. RESUS-BAY-01, ISO-ROOM-01)"
    )
    resource_type: str = Field(
        ..., description="RESUS_BAY, ISOLATION_ROOM, OPD_CHAMBER, or STANDARD_WAITING"
    )
    porter_ticket_id: str | None = Field(
        default=None, description="Dispatched wheelchair porter ticket (e.g. PORTER-1234)"
    )
    isolation_precaution: str | None = Field(
        default=None, description="Infection precaution e.g. AIRBORNE_CONTACT"
    )
    instructions_en: str
    instructions_hi: str
    allocated_at: str
    message: str


class BayStatus(BaseModel):
    """Real-time status of a single Resuscitation Bay."""

    bay_id: str
    is_occupied: bool
    assigned_session_id: UUID | None = None


class IsolationRoomStatus(BaseModel):
    """Real-time status of a single Negative-Pressure Isolation Room."""

    room_id: str
    is_occupied: bool
    assigned_session_id: UUID | None = None
    precaution: str | None = None


class PorterTicketStatus(BaseModel):
    """Real-time status of an active wheelchair / stretcher porter ticket."""

    ticket_id: str
    session_id: UUID
    status: str = "DISPATCHED"
    created_at: str


class ResourceStatusResponse(BaseModel):
    """Live occupancy and dispatch status grid across all hospital facility resources."""

    resus_bays: list[BayStatus]
    isolation_rooms: list[IsolationRoomStatus]
    active_porters: list[PorterTicketStatus]
    total_resus_occupied: int
    total_isolation_occupied: int
    total_active_porters: int
