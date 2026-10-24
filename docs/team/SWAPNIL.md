# Swapnil — ML/AI and CardioVision Lead

## Mission

Turn CardioVision and future screening models into reproducible, explainable,
calibration-aware capabilities with safe product boundaries.

## Owns

- `models/` and `eval/`.
- Model manifests, model cards, evaluation reports, thresholds, and rollback
  metadata.
- CardioVision explanation payloads and deterministic model fixtures.
- Future Blender/GLB explainability planning with Soumyadeep.
- Model registry design after CardioVision evidence is stable.

## Must review

- Any claim about AUC, accuracy, calibration, subgroup performance, or risk.
- Feature preprocessing and missing-data behavior.
- Clinical-review thresholds and interactions with the veto engine.
- 3D visual mappings that could imply unsupported clinical causality.

## SEVA deliverables

- Synthetic/approved-data evaluation methodology.
- Model manifest and model card.
- Deterministic regression cases.
- Visible model/version/limitation metadata.
- A report explicitly labeled **not clinical validation** unless external evidence
  exists.

## Competition launch

- First packet: [F-001 — CardioVision Handoff Evidence](../tasks/active/F-001-cardiovision-handoff-evidence.md).
- Follow-on packet: [F-004 — CardioVision Model Evidence](../tasks/active/F-004-cardiovision-model-evidence.md).
- Review gate: Soham approves safety/claim language and Pabitra confirms
  reproducibility before any model metric or threshold is published.

## Stop conditions

Stop when data provenance is unclear, metrics cannot be reproduced, an animation
overstates a model explanation, or a model output would trigger a consequential
action without clinician review.
