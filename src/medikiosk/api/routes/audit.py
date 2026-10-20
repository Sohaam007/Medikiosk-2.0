"""Audit chain verification and forensic ledger API routes.

Provides cryptographic verification of SHA-256 Merkle hash chains
from GENESIS_HASH ("0"*64) to head_hash, detecting sequence-level tampering.

SECURITY:
    Zero PHI. No patient identifiers or payloads are exposed.
    Only session IDs, cryptographic hashes, sequence counts, and status flags are returned.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from medikiosk.api.dependencies.container import get_session_service_dep
from medikiosk.api.schemas.audit import AuditChainVerificationResponse, VerifyChainResponse
from medikiosk.domain.audit_chain import verify_audit_chain
from medikiosk.domain.errors import SessionNotFoundError
from medikiosk.services.session_service import SessionService

log = structlog.get_logger(__name__)

router = APIRouter(tags=["audit"])

SessionServiceDep = Annotated[SessionService, Depends(get_session_service_dep)]

# Re-export for convenience
__all__ = ["AuditChainVerificationResponse", "VerifyChainResponse", "router"]


@router.get(
    "/api/audit/verify-chain/{session_id}",
    response_model=VerifyChainResponse,
    status_code=200,
)
async def verify_chain(
    session_id: UUID,
    session_svc: SessionServiceDep,
) -> VerifyChainResponse:
    """Verify cryptographic SHA-256 Merkle hash chain continuity for a session audit ledger.

    Returns 200 with verification details if valid, or identifies exact broken_at_seq if tampered.
    Raises 404 if the session ID is not found.
    """
    try:
        await session_svc.get_session(session_id)
    except SessionNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        ) from err

    events = await session_svc._audit_repo.list_for_session(session_id)
    result = verify_audit_chain(events)

    if result.is_valid:
        summary_msg = f"Audit ledger verified successfully: {result.checked_events} events intact"
    else:
        summary_msg = (
            f"Audit ledger integrity failure: chain broken at sequence {result.broken_at_seq}"
        )

    log.info(
        "audit_chain_verified",
        session_id=str(session_id),
        is_valid=result.is_valid,
        checked_events=result.checked_events,
        broken_at_seq=result.broken_at_seq,
    )

    return VerifyChainResponse(
        session_id=session_id,
        is_valid=result.is_valid,
        checked_events=result.checked_events,
        genesis_hash=result.genesis_hash,
        head_hash=result.head_hash,
        broken_at_seq=result.broken_at_seq,
        message=summary_msg,
    )
