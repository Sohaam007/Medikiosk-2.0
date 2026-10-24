# F-006 — Care Navigator Workspace and Referral Outcome Tracking

## Identity

- Feature: Care navigator workspace and referral outcome tracking
- Phase: Track B — Product Scale, B1/B4 foundation
- Owner: Soham
- Reviewer: Soumyadeep and Pabitra
- Branch: `feat/f006-care-navigator`

## User outcome

An authorized clinician or care navigator can preserve the workflow state of a
local, non-binding referral candidate and see its current status without the
system claiming that treatment occurred or that a provider confirmed capacity.

## Current evidence

- Existing entry points:
  - `POST /api/screening/cardiovascular/referral`
  - `GET /api/clinician/queue`
  - `GET /api/clinician/session/{session_id}`
- Existing contracts/ports:
  - `ReferralRecommendation`
  - `SessionRepository`
  - `AuditRepository`
  - `CachePort`
- Existing persistence:
  - SQLAlchemy models under `src/medikiosk/adapters/database/`
  - local startup `Base.metadata.create_all`
- Existing safety boundary:
  - ADR 0009 — referral candidates are non-binding.
  - Existing veto engine and intake cache hold critical alerts.
- Relevant tests:
  - `tests/unit/domain/test_referral_matcher.py`
  - `tests/e2e/test_screening_api.py`
  - `tests/e2e/test_clinician_api.py`
  - `tests/invariants/test_audit_trail.py`

## Scope

- Allowed paths:
  - `src/medikiosk/domain/contracts/`
  - `src/medikiosk/domain/`
  - `src/medikiosk/ports/`
  - `src/medikiosk/services/`
  - `src/medikiosk/adapters/database/`
  - `src/medikiosk/api/`
  - `tests/unit/`, `tests/integration/`, `tests/e2e/`, `tests/invariants/`
  - `docs/FEATURES.md`
  - `docs/REGRESSION.md`
  - `docs/STATUS.md`, only for verified current-state changes
  - `docs/INTEGRATIONS.md`, only if integration truth changes
  - `docs/decisions/0014-care-navigator-referral-outcomes.md`
  - this task packet
  - generated `docs/openapi.json` and `frontend/src/client/` only after source
    API changes, using the prescribed generation commands
- Forbidden paths:
  - `backend/`, `core/`, `server/`, and `kiosk/`
  - provider adapters, messaging, booking, payment, capacity, or external APIs
  - `models/` and CardioVision thresholds
  - raw patient data, free-text navigator notes, secrets, and credentials
- Explicitly out of scope:
  - frontend care-navigator UI in this first backend slice
  - patient-facing referral status
  - treatment or clinical outcome recording
  - provider availability or live hospital routing
  - WhatsApp/SMS/email delivery
  - database migration tooling itself

## Contract and safety

- Workflow statuses: `recommended`, `reviewed`, `contacted`, `attended`,
  `declined`.
- Allowed transitions:
  - `recommended → reviewed`
  - `reviewed → contacted`
  - `contacted → attended`
  - `contacted → declined`
- A status is workflow metadata only; it is never a diagnosis, treatment result,
  appointment confirmation, or provider-capacity claim.
- Only `Triage_Nurse` and `Attending_Physician` may write or transition records.
- Critical-veto sessions are rejected from routine referral tracking.
- Audit payloads contain opaque IDs, prior/new status, and actor role only.
- No external egress is introduced. Local SQLite and deterministic test fakes
  are the only supported modes.

## Acceptance criteria

- [ ] Domain contract validates statuses and legal transitions.
- [ ] Invalid, terminal, backward, and skipped transitions are rejected.
- [ ] Referral records preserve session and candidate IDs without PHI.
- [ ] Create and transition operations append audit events before success is
      returned.
- [ ] Critical-veto sessions cannot create or transition routine outcomes.
- [ ] Clinician-only authorization is enforced on write routes.
- [ ] List/read responses expose workflow metadata only and use deterministic
      ordering.
- [ ] SQLite integration creates and reads the new table through the existing
      local bootstrap.
- [ ] OpenAPI and generated client are synchronized after route changes.
- [ ] Existing CardioVision, clinician queue, audit, and full backend tests pass.
- [ ] No live-provider, treatment-outcome, booking, payment, or capacity claim is
      introduced.

## Verification

- Focused unit command:
  - `uv run --extra dev python -m pytest tests/unit/domain/test_referral_outcomes.py tests/unit/services/test_referral_outcome_service.py -q`
- Focused API/integration command:
  - `uv run --extra dev python -m pytest tests/e2e/test_referral_outcomes_api.py tests/integration/test_referral_outcomes.py -q`
- Generated contract commands:
  - `uv run --extra dev python scripts/export_openapi.py`
  - `cd frontend && npm run generate-client`
- Downstream commands:
  - `uv run --extra dev ruff check src/ tests/`
  - `uv run --extra dev ruff format --check src/ tests/`
  - `uv run --extra dev mypy src/ --strict`
  - `uv run --extra dev python -m pytest tests/ -q`
  - `cd frontend && npm run lint && npm run build`
  - `python scripts/check_repo_hygiene.py`
  - `git diff --check`
- Manual check:
  - Use clinician auth to create and transition a synthetic referral, confirm
    audit/readback behavior, and verify that kiosk auth is rejected.

## Rollback

Revert the F-006 commit and disable the new routes. The existing CardioVision
non-binding candidate endpoint remains available. In a future migration-managed
environment, remove the table only through a reviewed forward migration.

## Documentation updates

- [ ] `docs/FEATURES.md`
- [ ] `docs/REGRESSION.md`
- [ ] `docs/STATUS.md`
- [ ] `docs/decisions/0014-care-navigator-referral-outcomes.md`
