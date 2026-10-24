# MediKiosk 2.0 — Regression Map

**Role:** changed-module to downstream-verification map.

This ledger prevents a change from being declared safe after only its nearest
unit tests pass. Update the row when a module gains a new consumer or a new
executable acceptance command.

| Changed area | Downstream consumers | Required evidence |
|---|---|---|
| `src/medikiosk/domain/contracts/` | API schemas, OpenAPI, generated TypeScript client, repositories | Contract tests, OpenAPI export, client generation, full backend suite, frontend build. |
| `src/medikiosk/domain/intake/` | `src/medikiosk/services/intake_service.py`, intake routes, kiosk view, summary generation | Intake unit tests, `tests/e2e/test_intake_api.py`, full backend suite. |
| `src/medikiosk/domain/triage/`, `src/medikiosk/domain/vitals.py`, `src/medikiosk/domain/veto.py` | intake flow, clinician queue, emergency UI, commercial-flow guard | Invariant/chokepoint tests, phase route tests, full backend suite. |
| `src/medikiosk/domain/referral_matcher.py` | cardiovascular referral route, CardioVision panel | Matcher unit tests, screening API tests, inspect non-binding behavior. |
| `src/medikiosk/domain/contracts/referral_outcome.py`, referral outcome policy, and F-006 service | care navigator status routes, audit trail, local referral workflow | Domain transition tests, service/audit tests, clinician authorization tests, referral-outcome API tests, full backend suite. |
| `src/medikiosk/adapters/cardiovision/` | screening routes, referral route, model output UI | Adapter tests, screening E2E tests, mode-specific smoke test. |
| `src/medikiosk/services/ocr_service.py` | document upload route, document repository, clinician document view | Document E2E tests, adapter tests, upload-limit tests. |
| `src/medikiosk/services/summary_service.py` | summary and FHIR routes, clinician view, generated client | Summary E2E tests, contract review, FHIR claim review. |
| `src/medikiosk/api/routes/` | OpenAPI, generated client, frontend calls, auth policy | Route tests, OpenAPI export, SDK generation, frontend build. |
| `src/medikiosk/api/dependencies/container.py` | every route using an injected adapter/service | Focused route tests, full suite, inspect mock/live mode selection. |
| `src/medikiosk/adapters/database/` or migrations | all persisted services and startup lifecycle | Integration tests, clean database initialization, full suite. |
| `frontend/src/client/` | all API-consuming frontend features | Regenerate from OpenAPI; frontend lint/build. |
| `frontend/src/views/KioskIntakeView.tsx` | kiosk journey, browser APIs, offline state, accessibility | Frontend lint/build, manual kiosk smoke, focused browser test when available. |
| `frontend/src/views/ClinicianQueueView.tsx` | queue, documents, FHIR download, integrations UI | Frontend lint/build, clinician smoke, accessibility review. |
| `frontend/src/index.css` or theme tokens | every frontend surface | Frontend build, visual/a11y review, touch-target audit if interaction sizing changes. |
| `models/` or model inference code | screening APIs, model cards, clinical review policy | Model contract tests, evaluation report, calibration/subgroup checks. |
| Future Blender asset sources, visualization assets, or scene manifests | explanation service, GLB viewer, static fallback, assistant scene selection | Clean Blender export, manifest/checksum validation, GLB load smoke, static/text equivalence, frontend build, performance/a11y/reduced-motion review. |
| assistant adapter or explanation service | intake flow, screening explanation, clinician summary, PHI-egress boundary | Schema validation, allowlisted-action tests, red-flag/veto tests, provider timeout/failure tests, offline fallback, full backend suite, frontend smoke. |
| `scripts/export_openapi.py` | generated API contract and TypeScript SDK | Export diff inspection, client generation, frontend build. |
| `tests/`, `.github/workflows/`, and release evidence | PR checks, clean-clone setup, demo submission | Full verification matrix, hygiene, diff review, smoke/evidence inventory, and human release review. |

## Minimum post-change matrix

### Backend-only change

```text
focused pytest → invariants → ruff → format check → mypy → full pytest
```

### API/contract change

```text
focused pytest → export OpenAPI → generate client → backend checks → frontend build
```

### Frontend change

```text
focused UI check → npm lint → npm build → accessibility/manual smoke
```

### Integration change

```text
mock contract test → failure/timeout test → auth/PHI review → full suite
→ sandbox evidence if credentials are available
```

### Model change

```text
contract test → deterministic regression set → calibration/subgroup evaluation
→ safety-threshold review → API/UI smoke
```

### 3D or assistant change

```text
scene/explanation contract → deterministic mock → safety/PHI review
→ GLB or provider failure tests → frontend build → accessibility/performance
→ static fallback smoke → full regression matrix
```

## Regression record template

When a change affects an existing row, add a dated note to the feature handoff
or PR description:

```text
Change:
Affected row(s):
Focused command:
Downstream commands:
Observed exit codes:
Generated artifacts:
Remaining risk:
```
