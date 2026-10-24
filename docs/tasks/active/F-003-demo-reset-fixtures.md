# F-003 — Deterministic Synthetic Demo Reset and Failure Fixtures

## Identity

- Feature: Deterministic synthetic demo reset and failure fixtures
- Phase: Track A — SEVA Demo Release
- Owner: Aditya
- Reviewer: Pabitra and Soham
- Branch: `feat/f003-demo-reset-fixtures`

## User outcome

The five-minute demo can be reset to a known synthetic state and can visibly
demonstrate offline, auth-failure, timeout, and provider-capable boundaries
without sending real patient data or pretending that a mock delivered externally.

## Current evidence

- Existing local adapters: CardioVision, OCR/LLM boundary, PM-JAY mock,
  WhatsApp mock, local doctor/package catalogs, cache, and database bootstrap.
- Existing evidence owners: `docs/INTEGRATIONS.md`, `docs/UNVERIFIED.md`,
  `docs/DEMO_EVIDENCE.md`.
- Existing tests: adapter integration tests, API tests, and stack-flow tests.

## Scope

- Allowed paths: synthetic fixtures, reset/demo scripts, adapter boundary tests,
  `docs/INTEGRATIONS.md`, `docs/UNVERIFIED.md`, `docs/DEMO_EVIDENCE.md`, and
  this packet.
- Forbidden paths: real patient data, credentials, external calls, legacy trees,
  clinical thresholds, provider promotion, and unreviewed API contract changes.
- Out of scope: live ABDM, PM-JAY, WhatsApp, payment, hospital capacity,
  ambulance, travel, or messaging delivery.

## Contract and safety

- Fixtures must use opaque UUIDs and synthetic values only.
- Reset must be idempotent and leave the same demo case every time.
- Failure fixtures must fail closed and use explicit local/mock/provider-capable
  labels.
- Webhook/SSE fixtures must document replay/auth behavior; no raw payload logging.
- Any external adapter remains disabled unless separately configured and reviewed.

## Acceptance criteria

- [ ] One documented synthetic demo manifest exists.
- [ ] Reset can be run repeatedly without accumulating sessions or audit drift.
- [ ] CardioVision, OCR, referral, PM-JAY, and communications failure cases are
      deterministic and covered by tests.
- [ ] Offline/auth failure is visibly distinct from successful provider delivery.
- [ ] Integration matrix and unverified log match executable behavior.
- [ ] No fixture contains names, phone numbers, ABHA/Aadhaar IDs, or raw PHI.

## Verification

- Focused adapter and integration tests for each fixture family.
- Full backend suite and repository hygiene.
- Manual reset-repeat-reset smoke with the local launcher.
- Pabitra reviews reproducibility; Soham reviews claims and external-egress
  boundaries.

## Rollback

Disable the new fixture/reset path and retain the existing deterministic local
demo. Remove any fixture that cannot be proven synthetic and repeatable.

## Handoff

Return the manifest, reset command, fixture inventory, failure matrix, exact test
commands, and known limitations to Pabitra and Soham.
