# F-004 — CardioVision Model Card, Evaluation, and Limitation Evidence

## Identity

- Feature: CardioVision model card, evaluation, and limitation evidence
- Phase: Track A — SEVA Demo Release
- Owner: Swapnil
- Reviewer: Soham and Pabitra
- Branch: `feat/f004-cardiovision-model-evidence`

## User outcome

Reviewers can distinguish the local CardioVision model artifact, its measured
offline behavior, its limitations, and the evidence that is still unavailable
before any clinical or production claim is considered.

## Current evidence

- Governance: `docs/MODEL_GOVERNANCE.md`.
- Assets: `models/cardiovision/` manifest-like JSON, boosters, calibration, and
  synthetic/demo holdout data.
- Evaluation surface: `eval/` with synthetic corpora and metric modules.
- Runtime boundary: CardioVision adapter and screening contract.

## Scope

- Allowed paths: `models/cardiovision/`, `eval/`, model-focused tests, model
  card/evaluation documentation, and this packet.
- Forbidden paths: clinical threshold changes without Soham approval, raw or
  identifiable data, provider integrations, frontend API changes, and claims not
  supported by reproducible output.
- Out of scope: clinical validation, regulatory classification, real-patient
  pilot approval, new disease models, and hosted AI assistant behavior.

## Contract and safety

- Every report records model ID/version, inputs, preprocessing, missing-data
  behavior, provenance, seed, environment, command, output checksum, and limits.
- AUC/accuracy/calibration numbers are evidence labels, not product promises.
- Screening probability is not diagnosis and cannot override deterministic veto.
- Invalid or missing inputs must remain explicit and fail closed to review.
- No raw patient or model payloads enter logs or committed evidence.

## Acceptance criteria

- [ ] Model card and manifest are complete against `docs/MODEL_GOVERNANCE.md`.
- [ ] Offline evaluation is reproducible from synthetic/approved data.
- [ ] Calibration, subgroup, invalid-input, and missing-data limitations are
      either measured or explicitly marked unavailable.
- [ ] Rollback artifact/version is named.
- [ ] The report says **not clinical validation** unless qualified external
      evidence is added.
- [ ] Soham approves safety/claim wording and Pabitra verifies reproducibility.

## Verification

- Exact offline evaluation command recorded in the report.
- CardioVision adapter/referral/screening tests.
- Full backend quality checks and repository hygiene.
- Manual comparison of model metadata shown in the UI against the manifest.

## Rollback

Revert to the last accepted local model artifact or deterministic mock mode.
Remove unsupported metrics rather than weakening the claim boundary.

## Handoff

Return the model card, manifest, evaluation report, checksums, command output,
limitations, and promotion recommendation to Soham and Pabitra.
