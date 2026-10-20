"""Ports for model-backed screening services."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from medikiosk.domain.contracts.cardiovascular import CardiovascularScreeningResult


class CardiovascularScreeningPort(Protocol):
    """Stable boundary between the intake API and a screening engine."""

    def predict(self, features: Mapping[str, Any]) -> CardiovascularScreeningResult:
        """Return a safe, explainable cardiovascular screening result."""
