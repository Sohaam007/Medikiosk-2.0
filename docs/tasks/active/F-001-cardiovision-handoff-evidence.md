# F-001 — CardioVision Screening to Clinician Handoff Evidence

## Identity

- Feature: CardioVision screening to clinician handoff
- Phase: Track A — SEVA Demo Release
- Owner: Swapnil
- Reviewer: Soham and Pabitra
- Branch: `feat/f001-cardiovision-evidence`

## User outcome

The team can demonstrate a reproducible CardioVision screening-to-clinician
handoff using synthetic inputs, with model/version metadata, explanations,
missing-input behavior, and an explicit clinician-review boundary.

## Current evidence

- Runtime: `src/medikiosk/adapters/cardiovision/`, screening route, referral route.
- UI: `frontend/src/components/CardioVisionPanel.tsx`.
- Contracts: `CardiovascularScreeningResult`, `ReferralRecommendation`.
- Tests: CardioVision adapter, referral matcher, screening API, invariants.
- Canonical boundaries: ADR 0008, ADR 0009, F-010 claim matrix.

## Scope

- Allowed paths: `models/cardiovision/`, `eval/`, CardioVision-focused tests,
  `docs/SEVA_SUBMISSION.md`, `docs/DEMO_EVIDENCE.md`, and this packet.
- Forbidden paths: clinical thresholds without approval, provider integrations,
  patient data, frontend API contracts, payment/booking/capacity behavior, and
  legacy runtime trees.
- Out of scope: new diseases, calibration claims without evidence, diagnosis,
  emergency disposition, or live-provider promotion.

## Contract and safety

- Preserve the existing screening contract and clinician-review requirement.
- Use synthetic or approved de-identified data only.
- Report local mock/local-model mode accurately; do not call it clinical
  validation or verified live connectivity.
- Keep deterministic veto behavior authoritative over model output.
- Do not log features, raw model output, or patient data.

## Acceptance criteria

- [ ] Model manifest identifies model ID/version, input schema, mode, checksum,
      missing-data behavior, and rollback reference.
- [ ] Model card records limitations and explicitly says not clinical validation.
- [ ] Deterministic positive, low-risk, invalid-input, and missing-input cases
      are reproducible offline.
- [ ] Referral output remains non-binding and clinician-reviewed.
- [ ] Evidence includes exact commands, fixture source, environment, and gaps.
- [ ] No unsupported AUC, calibration, threshold, or subgroup claim is published.

## Verification

- Focused: `uv run --extra dev python -m pytest tests/unit/adapters/test_cardiovision_adapter.py tests/unit/domain/test_referral_matcher.py tests/e2e/test_screening_api.py -q`
- Model evidence: record the exact offline evaluation command, seed, and output
  checksum in the model report.
- Downstream: full backend suite, Ruff, format check, strict mypy, frontend
  lint/build, and repository hygiene.
- Manual: inspect the CardioVision panel for mode/version/disclaimer labels.

## Rollback

Remove unverified evidence artifacts and revert to deterministic mock mode. Do
not alter the existing screening contract or promote the local model.

## Handoff

Return the model card, manifest/evaluation files, command output, limitations,
and unresolved-risk list to Soham and Pabitra. F-004 may consume these outputs;
no clinical claim is authorized by this packet alone.
