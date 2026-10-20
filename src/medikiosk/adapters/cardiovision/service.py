"""CardioVision adapter with deterministic offline and optional real-model modes.

The default ``mock`` mode is intentionally offline so a kiosk demo and the test
suite never need a model download or a network call. ``real`` mode loads the
versioned XGBoost assets copied from the CardioVision project.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from medikiosk.domain.contracts.cardiovascular import (
    CardiovascularScreeningResult,
    ExplanationItem,
    RiskEstimate,
    VesselRisk,
)
from medikiosk.domain.errors import ValidationError


class CardioVisionAdapter:
    """Run CardioVision without leaking model-specific details into the API."""

    def __init__(self, mode: str = "mock", model_dir: str | Path | None = None) -> None:
        self.mode = mode.lower().strip()
        default_dir = Path(__file__).resolve().parents[4] / "models" / "cardiovision"
        self.model_dir = Path(model_dir) if model_dir is not None else default_dir
        self._feature_names = self._read_json("feature_names.json", [])
        schema = self._read_json("feature_schema.json", [])
        self._defaults = {item["name"]: item.get("default", 0) for item in schema}

    def predict(self, features: Mapping[str, Any]) -> CardiovascularScreeningResult:
        """Validate feature names and run the configured screening engine."""
        feature_values = dict(features)
        unknown = sorted(set(feature_values) - set(self._feature_names))
        if unknown:
            raise ValidationError("Unknown cardiovascular screening feature")
        if self.mode == "real":
            return self._predict_real(feature_values)
        return self._predict_mock(feature_values)

    def _read_json(self, name: str, fallback: Any) -> Any:
        path = self.model_dir / name
        if not path.exists():
            return fallback
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _value(self, features: dict[str, Any], name: str, default: float) -> float:
        try:
            return float(features.get(name, self._defaults.get(name, default)))
        except (TypeError, ValueError):
            return default

    def _predict_mock(self, features: dict[str, Any]) -> CardiovascularScreeningResult:
        """Use the CardioVision demo equation for offline, explainable runs."""
        age = self._value(features, "Age", 58)
        bp = self._value(features, "BP", 130)
        ldl = self._value(features, "LDL", 100)
        ef = self._value(features, "EF-TTE", 50)
        htn = self._value(features, "HTN", 0)
        smoker = self._value(features, "Current Smoker", 0)
        diabetes = self._value(features, "DM", 0)
        chest_pain = self._value(features, "Typical Chest Pain", 0)
        logit = (
            -1.4
            + 0.045 * (age - 55)
            + 0.015 * (ldl - 100)
            + 0.018 * (bp - 120)
            - 0.045 * (ef - 50)
            + 0.70 * htn
            + 0.55 * smoker
            + 0.50 * diabetes
            + 0.65 * chest_pain
        )
        cad = self._sigmoid(logit)
        lad = self._sigmoid(logit - 0.20)
        lcx = self._sigmoid(logit - 0.70)
        rca = self._sigmoid(logit - 0.60)
        max_vessel = max(lad, lcx, rca)
        adjusted = max_vessel > cad
        cad = max(cad, max_vessel)
        contributions = [
            ("Age", age, 0.045 * (age - 55)),
            ("Typical Chest Pain", chest_pain, 0.65 * chest_pain),
            ("HTN", htn, 0.70 * htn),
            ("EF-TTE", ef, -0.045 * (ef - 50)),
            ("LDL", ldl, 0.015 * (ldl - 100)),
            ("BP", bp, 0.018 * (bp - 120)),
            ("Current Smoker", smoker, 0.55 * smoker),
            ("DM", diabetes, 0.50 * diabetes),
        ]
        items = [
            ExplanationItem(feature=name, value=value, shap=round(shap, 4))
            for name, value, shap in sorted(
                contributions, key=lambda item: abs(item[2]), reverse=True
            )
        ]
        explanation = dict.fromkeys(("CAD", "LAD", "LCX", "RCA"), items)
        return CardiovascularScreeningResult(
            cad=RiskEstimate(prob=round(cad, 4), label=int(cad >= 0.5), ci=self._ci(cad)),
            vessels={
                "LAD": VesselRisk(prob=round(lad, 4), label=int(lad >= 0.5)),
                "LCX": VesselRisk(prob=round(lcx, 4), label=int(lcx >= 0.5)),
                "RCA": VesselRisk(prob=round(rca, 4), label=int(rca >= 0.5)),
            },
            explanations=explanation,
            meta={
                "model_version": "cardiovision-demo-v1",
                "mode": "mock",
                "cad_adjusted": adjusted,
                "disclaimer": "Screening support only; clinician review is required.",
            },
        )

    def _predict_real(self, features: dict[str, Any]) -> CardiovascularScreeningResult:
        """Run the copied CardioVision XGBoost assets when explicitly enabled."""
        try:
            import numpy as np
            import xgboost as xgb
        except ImportError as exc:
            raise RuntimeError("Real CardioVision mode requires numpy and xgboost") from exc

        calibration = self._read_json("calibration.json", {})
        matrix_values = [self._encode(features, name) for name in self._feature_names]
        matrix = np.array([matrix_values], dtype=np.float32)
        dmatrix = xgb.DMatrix(matrix, feature_names=self._feature_names)
        probs: dict[str, float] = {}
        explanations: dict[str, list[ExplanationItem]] = {}
        for target in ("cad", "lad", "lcx", "rca"):
            booster = xgb.Booster()
            booster.load_model(str(self.model_dir / f"booster_{target}.json"))
            margin = float(booster.predict(dmatrix, output_margin=True)[0])
            params = calibration[target]
            probs[target] = self._sigmoid(float(params["A"]) * margin + float(params["B"]))
            contributions = booster.predict(dmatrix, pred_contribs=True)[0][:-1] * float(
                params["A"]
            )
            ranked = sorted(
                enumerate(contributions), key=lambda item: abs(float(item[1])), reverse=True
            )[:15]
            explanations[target.upper()] = [
                ExplanationItem(
                    feature=self._feature_names[index],
                    value=features.get(
                        self._feature_names[index],
                        self._defaults.get(self._feature_names[index], 0),
                    ),
                    shap=round(float(value), 4),
                )
                for index, value in ranked
            ]
        vessel_max = max(probs["lad"], probs["lcx"], probs["rca"])
        cad_adjusted = vessel_max > probs["cad"]
        cad = max(probs["cad"], vessel_max)
        return CardiovascularScreeningResult(
            cad=RiskEstimate(prob=round(cad, 4), label=int(cad >= 0.5), ci=self._ci(cad)),
            vessels={
                name.upper(): VesselRisk(prob=round(probs[name], 4), label=int(probs[name] >= 0.5))
                for name in ("lad", "lcx", "rca")
            },
            explanations=explanations,
            meta={
                "model_version": "cardiovision-assets-v1",
                "mode": "real",
                "cad_adjusted": cad_adjusted,
                "disclaimer": "Screening support only; clinician review is required.",
            },
        )

    def _encode(self, features: dict[str, Any], name: str) -> float:
        value = features.get(name, self._defaults.get(name, 0))
        if name == "Sex":
            return float(str(value).lower() == "male" or value == 1)
        mappings = {
            "BBB": {"N": 0.0, "LBBB": 1.0, "RBBB": 2.0},
            "VHD": {"N": 0.0, "MILD": 1.0, "MODERATE": 2.0, "SEVERE": 3.0},
        }
        if name in mappings:
            return mappings[name].get(str(value).strip().upper(), 0.0)
        return self._value(features, name, 0.0)

    @staticmethod
    def _sigmoid(value: float) -> float:
        return 1.0 / (1.0 + math.exp(-max(-35.0, min(35.0, value))))

    @staticmethod
    def _ci(probability: float) -> tuple[float, float]:
        return (round(max(0.01, probability - 0.08), 4), round(min(0.99, probability + 0.08), 4))
