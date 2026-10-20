"""Pydantic schemas for the Audit & Forensic Chain endpoints.

Covers:
- GET /api/audit/verify-chain/{session_id}

SECURITY: Zero PHI. Only cryptographic hashes, sequence counts, and status flags.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class AuditChainVerificationResponse(BaseModel):
    """Response schema for GET /api/audit/verify-chain/{session_id}."""

    session_id: UUID = Field(..., description="Target session identifier")
    is_valid: bool = Field(..., description="Whether the cryptographic hash chain is intact")
    checked_events: int = Field(..., description="Total count of audit events verified")
    genesis_hash: str = Field(..., description="Root SHA-256 genesis hash ('0'*64)")
    head_hash: str = Field(..., description="Latest verified block SHA-256 hash")
    broken_at_seq: int | None = Field(
        default=None, description="Sequence number where tampering was detected, or None"
    )
    message: str = Field(..., description="Forensic verification summary message")


# Canonical alias for compatibility
VerifyChainResponse = AuditChainVerificationResponse
