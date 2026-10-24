# F-010 — SEVA Demo Scope, Claim, and Acceptance Freeze

## Identity

- Feature: SEVA demo scope, claim, and acceptance freeze
- Phase: Track A — SEVA Demo Release
- Owner: Soham
- Reviewer: Soumyadeep and Pabitra
- Branch: `chore/pr-review-merge-policy`

## User outcome

The team has one explicit, reviewable boundary for the SEVA demonstration. The
CardioVision → intake → clinician handoff journey can proceed without adding
unsupported clinical, provider, production, or interoperability claims.

## Current evidence

- Entry points:
  - `docs/SEVA_SUBMISSION.md`
  - `docs/DEMO_EVIDENCE.md`
  - `docs/ROADMAP.md`
  - `src/medikiosk/api/routes/screening.py`
- Existing contracts/ports:
  - `CardiovascularScreeningPort`
  - `CardiovascularScreeningResult`
  - `CardiovascularReferralResponse`
- Callers:
  - CardioVision panel and clinician-facing screening/referral flow.
  - Local intake and clinician queue journey.
- Relevant tests:
  - `tests/e2e/test_screening_api.py`
  - `tests/unit/adapters/test_cardiovision_adapter.py`
  - `tests/unit/domain/test_referral_matcher.py`
  - `tests/invariants/`
- Relevant ADRs:
  - ADR 0008 — CardioVision screening boundary.
  - ADR 0009 — non-binding CardioVision referral policy.
  - ADR 0011 — five-person two-track delivery.
  - ADR 0012 — clinical and regulatory readiness gate.

## Scope

- Allowed paths:
  - `docs/FEATURES.md`
  - `docs/tasks/active/F-010-seva-scope-claim-freeze.md`
  - `docs/SEVA_SUBMISSION.md`
  - `docs/DEMO_EVIDENCE.md`
  - `docs/STATUS.md`, only when a verified current-state fact changes.
- Forbidden paths:
  - `backend/`, `core/`, `server/`, and `kiosk/`.
  - Runtime code, frontend code, model assets, generated clients, and OpenAPI
    artifacts unless a later approved unit explicitly changes its scope.
  - Secrets, real patient data, provider credentials, and external systems.
- Explicitly out of scope:
  - New clinical thresholds or model behavior.
  - New required API fields or persistence migrations.
  - Provider, sandbox, or live integration promotion.
  - Diagnosis, treatment, emergency dispatch, booking, payment, capacity,
    regulatory, or production-readiness claims.
  - Product Scale features F-005 through F-009.

## Contract and safety

- Request/response or domain shape: No contract, port, schema, or generated
  client changes are planned.
- Auth/role/consent: Existing route authentication and clinician-review gates
  remain unchanged.
- PHI/external egress: Documentation must continue to require synthetic data
  and local/mock behavior. No new egress is introduced.
- Offline/mock behavior: The frozen demo remains deterministic and visibly
  labeled as local/mock or provider-capable-but-unverified where applicable.
- Critical-veto behavior: Screening and referral language must not override the
  server-side critical veto path or imply emergency disposition from model
  probability alone.

## Acceptance criteria

- [ ] The Track A journey is frozen as language/informant selection →
      CardioVision screen → explanation/disclaimer → non-binding local
      candidates → intake/document path → clinician review → local
      FHIR-shaped handoff → reset/offline/auth-failure behavior.
- [ ] Every demonstrable capability has an honest implementation label:
      local, mock/simulated, provider-capable but unverified, sandbox-verified,
      or deferred.
- [ ] Screening is explicitly described as a review signal, never a diagnosis.
- [ ] Referral candidates remain non-binding and do not imply booking, payment,
      live capacity, or hospital selection.
- [ ] The claim matrix agrees across `docs/SEVA_SUBMISSION.md`,
      `docs/DEMO_EVIDENCE.md`, `docs/INTEGRATIONS.md`, and `docs/STATUS.md`.
- [ ] The Track A release gate identifies exact evidence owners and does not
      mark missing screenshots, recording, clean-clone proof, or clinical review
      as complete.

## Verification

- Focused command:
  - `python scripts/check_repo_hygiene.py`
  - `git diff --check`
- Downstream commands:
  - `uv run --extra dev python -m pytest tests/ -q`
  - `uv run --extra dev ruff check src/ tests/`
  - `uv run --extra dev ruff format --check src/ tests/`
  - `uv run --extra dev mypy src/ --strict`
  - `cd frontend && npm run lint`
  - `cd frontend && npm run build`
- Manual/browser check:
  - Review the frozen journey and claim labels against the local CardioVision
    route/referral behavior and the SEVA demo script.

## Track A acceptance gate and owner handoff

The SEVA demo cannot be reported ready until every gate below has dated evidence
or an explicit unresolved-risk note. A passing local test does not substitute for
missing presentation, clinical, or clean-clone evidence.

| Gate | Required evidence | Responsible owner | Required reviewer | Status at packet creation |
|---|---|---|---|---|
| Scope and claims | Frozen journey and claim matrix agree across canonical docs | Soham | Soumyadeep + Pabitra | Open until final review |
| CardioVision | Model/version/limitation evidence and deterministic evaluation record | Swapnil | Soham + Pabitra | Evidence pending |
| Synthetic reset and failure paths | Repeatable synthetic case, reset instructions, offline/auth-failure behavior | Aditya | Pabitra + Soham | Evidence pending |
| Kiosk and clinician flow | Accessible, responsive flow with no fake provider success | Soumyadeep | Soham + Pabitra | Evidence pending |
| Backend and frontend checks | Tests, Ruff, format, strict mypy, frontend lint/build | Pabitra | Soham | Baseline documented; rerun required for release |
| Runtime smoke | Launcher, backend, frontend, and CardioVision referral smoke | Pabitra | Soham + affected owner | Evidence pending |
| Submission artifacts | Dated screenshots, screen recording, judge summary, clean-clone log | Pabitra | Soham + Soumyadeep | Incomplete |
| Human review | Clinical/usability review plan recorded; no self-certification of pilot readiness | Soham | External reviewer required before pilot | Incomplete |

### Handoff constraints

- Swapnil may provide model evidence, but may not publish clinical-performance
  or threshold claims without Soham safety review and Pabitra reproducibility
  evidence.
- Aditya may provide fixtures and mock/provider seams, but may not promote an
  integration to sandbox or live status without the required boundary,
  contract, failure, and dated external evidence.
- Soumyadeep may polish the demo flow, but must preserve the claim labels,
  clinician-review boundary, and visible failure behavior.
- Pabitra may block release for missing evidence, broken reproducibility,
  security findings, or an unverified claim.
- No owner may mark F-001 or F-004 `Done` solely from a UI card, fixture,
  passing mock test, or local model run.

### Release decision

Soham gives the final scope and claim decision only after the required reviewers
have reviewed the evidence. This packet does not authorize a live-provider,
clinical-validation, regulatory, or production-readiness claim.

## Rollback

Revert the F-010 feature-register row and task packet. This is documentation-only
work and must not alter runtime behavior or the existing demo path.

## Documentation updates

- [ ] `docs/STATUS.md` — only if the verified evidence state changes
- [ ] `docs/REGRESSION.md`
- [ ] ADR/model/integration docs if required

## Unit sequence

1. F-010.1 — Register this packet and establish the bounded release-gate scope.
2. F-010.2 — Audit and reconcile the canonical Track A claim matrix.
3. F-010.3 — Finalize the acceptance gate and handoff requirements for the
   evidence, model, frontend, integration, and QA lanes.
