# ADR 0008: Bound CardioVision behind a screening port

## Decision

MediKiosk 2.0 exposes CardioVision through `CardiovascularScreeningPort` and a
single `POST /api/screening/cardiovascular` route. The copied CardioVision
assets live under `models/cardiovision` and are loaded only by the adapter.

The default mode is deterministic `mock`, which makes local demos and offline
tests reproducible. `CARDIOVISION_MODE=real` explicitly enables the versioned
XGBoost assets. Both modes return the same contract, include explanations, and
carry a screening-only disclaimer. The output is not a diagnosis and must be
reviewed by a clinician.

## Rationale

The SEVA plan requires screening to flow into MediKiosk intake and referral,
but importing CardioVision's standalone FastAPI application would create a
second runtime, duplicate authentication, and make offline demos fragile. A
port preserves the existing Clean Architecture and provides a stable seam for
the future referral matcher and 3D viewer.
