"""HTTP schemas for the CardioVision integration."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CardiovascularScreeningRequest(BaseModel):
    """Feature payload accepted from the kiosk or a clinician console."""

    model_config = ConfigDict(extra="forbid")

    features: dict[str, Any] = Field(min_length=1, max_length=64)
    session_id: UUID | None = None
