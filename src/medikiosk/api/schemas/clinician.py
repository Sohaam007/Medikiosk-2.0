"""Pydantic request/response schemas for the clinician API endpoints.

These schemas are the HTTP boundary layer only. Session IDs are the only
patient-scoped identifiers permitted. PHI MUST NOT appear in any field.
"""

from __future__ import annotations

import re
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class QueueEntry(BaseModel):
    """A single entry in the clinician triage queue.

    Attributes:
        session_id: Opaque session reference (no PHI).
        department_id: Clinical department this entry belongs to.
        triage_priority: Urgency level: critical|urgent|normal.
        wait_time_seconds: How long the patient has been waiting.
        status: Current lifecycle status of the session.
    """

    session_id: UUID
    department_id: str
    triage_priority: str = Field(description="critical|urgent|normal")
    wait_time_seconds: int = Field(ge=0)
    status: str


class QueueResponse(BaseModel):
    """Response body for GET /api/clinician/queue.

    Attributes:
        department_id: The department whose queue is returned.
        entries: Ordered list of queue entries (highest priority first).
        total_count: Total number of active sessions in the queue.
    """

    department_id: str
    entries: list[QueueEntry]
    total_count: int = Field(ge=0)


class PagePatientRequest(BaseModel):
    """Request to page a patient in the virtual waiting room."""

    session_id: UUID
    phone_number: str
    turns_ahead: int = Field(ge=0)

    @field_validator("phone_number")
    @classmethod
    def sanitize_phone(cls, v: str) -> str:
        """Strip spaces/dashes, validate, and enforce E.164 formatting."""
        if re.search(r"[a-zA-Z]", v):
            raise ValueError("Phone number must not contain letters")

        # Strip common formatting characters
        cleaned = re.sub(r"[\s\-\(\)]", "", v)

        # 10 digits -> default to India country code (+91)
        if len(cleaned) == 10 and cleaned.isdigit():
            cleaned = f"+91{cleaned}"
        # 11 digits starting with 0 -> replace leading 0 with +91
        elif len(cleaned) == 11 and cleaned.startswith("0") and cleaned[1:].isdigit():
            cleaned = f"+91{cleaned[1:]}"
        # 12 digits starting with 91 -> prepend +
        elif len(cleaned) == 12 and cleaned.startswith("91") and cleaned.isdigit():
            cleaned = f"+{cleaned}"

        # Strict E.164 validation: + followed by 7-15 digits
        if not re.match(r"^\+[1-9]\d{6,14}$", cleaned):
            raise ValueError("Phone number must be a valid E.164 format (e.g. +919876543210)")
        return cleaned


class PagePatientResponse(BaseModel):
    """Response for paging a patient."""

    paged: bool
    token: str
    turns_ahead: int


class ClinicianOverviewResponse(BaseModel):
    """Dashboard KPIs and red flags."""

    intakes_completed: int
    avg_intake_time_seconds: float
    documents_processed: int
    red_flags_caught: int
    active_red_flags: list[dict[str, object]]


class ClinicianSessionDetailResponse(BaseModel):
    """Full detail for a patient session."""

    session_id: str
    status: str
    token_number: str | None = None
    wait_time_seconds: int
    patient_profile: dict[str, object] | None = None
    chief_complaint: str | None = None
    triage_alerts: list[dict[str, object]]
    timeline_events: list[dict[str, object]]


# ── Phase X.3 Pharmacovigilance DDI & Safety Firewall Schemas ─────────────────


class SafetyAlertSchema(BaseModel):
    """Clinical safety alert schema for contraindications and precautions."""

    rule_id: str = Field(..., description="Safety rule identifier (e.g. RULE-DDI-001)")
    severity: str = Field(..., description="CRITICAL_CONTRAINDICATION, CAUTION, or INFO")
    title: str = Field(..., description="Short medical title of alert")
    clinical_detail: str = Field(
        ..., description="Detailed pharmacological mechanism and clinical hazard"
    )
    offending_agents: list[str] = Field(
        ..., description="List of interacting drugs or contraindicating conditions"
    )


class VerifyRxSafetyRequest(BaseModel):
    """Request body for POST /api/clinician/verify-rx-safety."""

    session_id: UUID = Field(..., description="Patient session UUID")
    prescribed_medications: list[str] = Field(
        ..., min_length=1, description="List of newly prescribed medications"
    )
    existing_medications: list[str] = Field(
        default_factory=list, description="List of existing or OCR-extracted medications"
    )
    allergies: list[str] = Field(
        default_factory=list, description="Patient declared drug allergies"
    )
    symptoms_text: str | None = Field(
        default=None, description="Optional symptoms text. PHI - never log."
    )


class VerifyRxSafetyResponse(BaseModel):
    """Response body for POST /api/clinician/verify-rx-safety."""

    session_id: UUID
    is_safe: bool
    severity: str = Field(..., description="SAFE, CAUTION, or CRITICAL_CONTRAINDICATION")
    alerts: list[SafetyAlertSchema]
    requires_override: bool
    evaluated_at: str
    message: str
