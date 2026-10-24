# F-011 — SEVA Release Evidence and Clean-Clone Verification

## Identity

- Feature: SEVA release evidence and clean-clone verification
- Phase: Track A — SEVA Demo Release
- Owner: Pabitra
- Reviewer: Soham and affected feature owner
- Branch: `chore/f011-seva-release-evidence`

## User outcome

The team can prove that the frozen SEVA demo is reproducible, resettable,
clinically bounded, and honestly documented before submission or public demo.

## Current evidence

- Canonical checklist: `docs/DEMO_EVIDENCE.md`.
- Frozen journey and claims: `docs/SEVA_SUBMISSION.md` and F-010.
- Verification commands: `docs/TESTS.md` and `docs/REGRESSION.md`.
- CI: `.github/workflows/` and PR checks.

## Scope

- Allowed paths: `tests/`, `.github/workflows/`, release/runbook/evidence docs,
  redacted evidence references/checksums, and this packet.
- Forbidden paths: real patient data, private tokens, unredacted screenshots,
  runtime behavior changes solely to make checks pass, direct merge, and claims
  not supported by executable evidence.
- Out of scope: new product capabilities, provider promotion, clinical
  validation, regulatory sign-off, and frontend/backend feature implementation.

## Contract and safety

- Evidence must record exact command, date, environment/mode, fixture class,
  result, generated artifacts, and remaining gap.
- Screenshots and recordings use synthetic data only and must show local/mock
  boundaries where relevant.
- A passing CI check does not close missing human review, clean-clone, or
  submission-artifact gates.
- Pabitra may block release for security, reproducibility, or claim failures.

## Acceptance criteria

- [ ] Full backend, frontend, lint, type, format, hygiene, and smoke results are
      captured with exit codes.
- [ ] Clean-clone setup and launcher/backend/frontend smoke are recorded.
- [ ] Reset, offline, auth-failure, and CardioVision failure paths are verified.
- [ ] Dated screenshots, screen recording, judge summary, and claim review are
      present or explicitly listed as unresolved.
- [ ] Evidence contains no PHI, secrets, tokens, or private payloads.
- [ ] Soham signs off claims/safety and affected owners sign off their artifacts.

## Verification

- Run the full matrix in `docs/TESTS.md` and affected rows in
  `docs/REGRESSION.md`.
- Inspect `git diff --check`, staged file list, and repository hygiene.
- Run clean-clone or equivalent reproducible setup on the pinned runtimes.
- Review the final evidence package against `docs/SEVA_SUBMISSION.md`.

## Rollback

Remove incomplete evidence references and keep the release blocked. Do not mark
the feature done or alter implementation to hide a failed check.

## Handoff

Return the verification table, evidence inventory, unresolved-risk list, and
release recommendation to Soham. Agents do not merge PRs.
