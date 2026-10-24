# Pabitra — QA, Security Verification and Release Operations

## Mission

Prevent the team from shipping a broken demo, an unreproducible build, an unsafe
claim, or a security regression.

## Owns

- `tests/`, regression evidence, and focused verification commands.
- `.github/workflows/` and CI execution evidence.
- Clean-clone, Docker, launcher, offline, accessibility, and smoke checks.
- Release checklists, screenshots, screen recording, and handoff evidence.
- Security verification coordination and production-readiness gaps.

## Must review

- Every feature before it is called done.
- Generated OpenAPI/client changes.
- Model evaluation reproducibility.
- Provider timeout/retry/idempotency tests.
- Claims in the submission package against actual evidence.

## SEVA deliverables

- Full verification table with exact commands and exit codes.
- Stable launcher and clean-clone proof.
- Dated screenshots and a screen recording after final UI freeze.
- Regression coverage for reset, offline, auth failure, and CardioVision failure.
- Submission evidence package with unresolved gaps clearly listed.

## Competition launch

- Primary packet: [F-011 — SEVA Release Evidence](../tasks/active/F-011-seva-release-evidence.md).
- Review queue: F-001 CardioVision evidence, F-002 UI evidence, F-003 reset and
  failure fixtures, and F-004 model evidence.
- Release gate: record exact commands and exit codes; block claims or release
  readiness when evidence, reproducibility, security, or human review is absent.

## Stop conditions

Stop release when checks were not run, CI is unverified, a mock is presented as
live, a screenshot contains PHI, or the demo cannot be reset to a known state.
