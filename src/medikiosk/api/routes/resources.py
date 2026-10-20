"""Facility Resources & Porter Orchestrator API routes.

Provides real-time acute trauma/resuscitation bay allocation, negative-pressure
isolation room routing, wheelchair porter dispatch, and live occupancy status grids.

SECURITY:
    Zero PHI. Symptoms and patient details are never logged.
    Only session IDs, resource codes, and operational flags are recorded.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from medikiosk.api.dependencies.container import get_session_service_dep
from medikiosk.api.schemas.resources import (
    AllocateResourceRequest,
    AllocateResourceResponse,
    BayStatus,
    IsolationRoomStatus,
    PorterTicketStatus,
    ResourceStatusResponse,
)
from medikiosk.domain.contracts.audit import AuditEvent, AuditEventType
from medikiosk.domain.contracts.session import SessionStatus
from medikiosk.domain.resource_allocator import (
    ISOLATION_ROOMS,
    RESUS_BAYS,
    ResourceAllocator,
)
from medikiosk.services.session_service import SessionService

log = structlog.get_logger(__name__)

router = APIRouter(tags=["resources"])

SessionServiceDep = Annotated[SessionService, Depends(get_session_service_dep)]


@router.post("/api/resources/allocate", response_model=AllocateResourceResponse, status_code=200)
async def allocate_resource(
    body: AllocateResourceRequest,
    session_svc: SessionServiceDep,
) -> AllocateResourceResponse:
    """Allocate resuscitation bay, isolation room, or OPD chamber and dispatch porter.

    Appends AuditEventType.RESOURCE_ALLOCATED with zero PHI.
    Persists allocated_resource_id and porter_ticket_id on the session.
    """
    session = await session_svc.get_session(body.session_id)
    if session.status == SessionStatus.TERMINATED:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Session has been terminated or purged",
        )

    # Determine currently occupied resources among active sessions
    active_sessions = await session_svc.list_active_sessions()
    occupied_resources: set[str] = {
        s.allocated_resource_id
        for s in active_sessions
        if s.allocated_resource_id and s.session_id != body.session_id
    }

    # Fallback to session risk band / NEWS2 if not explicitly provided in body
    triage_priority = body.triage_priority or session.news2_risk_band
    news2_score = body.news2_score if body.news2_score is not None else session.news2_score

    alloc = ResourceAllocator.allocate(
        triage_priority=triage_priority,
        news2_score=news2_score,
        symptoms_text=body.symptoms_text,
        needs_wheelchair=body.needs_wheelchair,
        session_id=body.session_id,
        occupied_resources=occupied_resources,
    )

    now = datetime.now(UTC)

    # Persist resource allocation on session entity
    updated_session = session.model_copy(
        update={
            "allocated_resource_id": alloc.resource_id,
            "porter_ticket_id": alloc.porter_ticket_id,
            "chamber_room": alloc.resource_id or session.chamber_room,
        }
    )
    await session_svc._session_repo.update(updated_session)

    # Append immutable audit trail event (Zero PHI)
    seq = await session_svc._next_seq(body.session_id)
    await session_svc._audit_repo.append(
        AuditEvent(
            event_id=uuid4(),
            session_id=body.session_id,
            event_type=AuditEventType.RESOURCE_ALLOCATED,
            timestamp=now,
            sequence_number=seq,
            payload={
                "resource_id": alloc.resource_id,
                "resource_type": alloc.resource_type,
                "porter_ticket_id": alloc.porter_ticket_id,
                "isolation_precaution": alloc.isolation_precaution,
            },
        )
    )

    log.info(
        "resource_allocated",
        session_id=str(body.session_id),
        resource_id=alloc.resource_id,
        resource_type=alloc.resource_type,
        porter_ticket_id=alloc.porter_ticket_id,
    )

    return AllocateResourceResponse(
        session_id=body.session_id,
        resource_id=alloc.resource_id,
        resource_type=alloc.resource_type,
        porter_ticket_id=alloc.porter_ticket_id,
        isolation_precaution=alloc.isolation_precaution,
        instructions_en=alloc.instructions_en,
        instructions_hi=alloc.instructions_hi,
        allocated_at=now.isoformat(),
        message=f"Resource allocation completed: {alloc.resource_type}",
    )


@router.get("/api/resources/status", response_model=ResourceStatusResponse, status_code=200)
async def get_resources_status(
    session_svc: SessionServiceDep,
    tenant_id: str = "default",
    department_id: str = "general",
) -> ResourceStatusResponse:
    """Return live occupancy grid of Resus Bays, Isolation Rooms, and active Porters."""
    active_sessions = await session_svc.list_active_sessions(
        tenant_id=tenant_id, department_id=department_id
    )

    occupied_resus: dict[str, UUID] = {}
    occupied_isolation: dict[str, tuple[UUID, str | None]] = {}
    active_porters: list[PorterTicketStatus] = []

    for s in active_sessions:
        if s.allocated_resource_id:
            res_id = s.allocated_resource_id
            if res_id.startswith("RESUS-BAY-"):
                occupied_resus[res_id] = s.session_id
            elif res_id.startswith("ISO-ROOM-"):
                occupied_isolation[res_id] = (s.session_id, "AIRBORNE_CONTACT")

        if s.porter_ticket_id:
            created_at_str = (
                s.created_at.isoformat()
                if hasattr(s.created_at, "isoformat")
                else str(s.created_at)
            )
            active_porters.append(
                PorterTicketStatus(
                    ticket_id=s.porter_ticket_id,
                    session_id=s.session_id,
                    status="DISPATCHED",
                    created_at=created_at_str,
                )
            )

    resus_bays: list[BayStatus] = [
        BayStatus(
            bay_id=bay,
            is_occupied=bay in occupied_resus,
            assigned_session_id=occupied_resus.get(bay),
        )
        for bay in RESUS_BAYS
    ]

    isolation_rooms: list[IsolationRoomStatus] = [
        IsolationRoomStatus(
            room_id=room,
            is_occupied=room in occupied_isolation,
            assigned_session_id=occupied_isolation[room][0] if room in occupied_isolation else None,
            precaution=occupied_isolation[room][1] if room in occupied_isolation else None,
        )
        for room in ISOLATION_ROOMS
    ]

    total_resus = sum(1 for b in resus_bays if b.is_occupied)
    total_iso = sum(1 for r in isolation_rooms if r.is_occupied)
    total_porters = len(active_porters)

    log.info(
        "resource_status_grid_queried",
        total_resus_occupied=total_resus,
        total_isolation_occupied=total_iso,
        total_active_porters=total_porters,
    )

    return ResourceStatusResponse(
        resus_bays=resus_bays,
        isolation_rooms=isolation_rooms,
        active_porters=active_porters,
        total_resus_occupied=total_resus,
        total_isolation_occupied=total_iso,
        total_active_porters=total_porters,
    )
