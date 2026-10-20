"""Immutable contracts for the CardioVision screening boundary."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RiskEstimate(BaseModel):
    """A calibrated risk estimate; it is not a diagnosis."""

    model_config = ConfigDict(frozen=True)

    prob: float = Field(ge=0.0, le=1.0)
    label: int = Field(ge=0, le=1)
    ci: tuple[float, float] | None = None


class VesselRisk(BaseModel):
    """Probability for a vessel-level screening target."""

    model_config = ConfigDict(frozen=True)

    prob: float = Field(ge=0.0, le=1.0)
    label: int = Field(ge=0, le=1)


class ExplanationItem(BaseModel):
    """A model contribution in calibrated log-odds space."""

    model_config = ConfigDict(frozen=True)

    feature: str
    value: Any
    shap: float


class CardiovascularScreeningResult(BaseModel):
    """CardioVision output shared by the API, UI, and referral workflow."""

    model_config = ConfigDict(frozen=True)

    cad: RiskEstimate
    vessels: dict[str, VesselRisk]
    explanations: dict[str, list[ExplanationItem]]
    meta: dict[str, object]
