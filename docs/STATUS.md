# MediKiosk 2.0 — Current Status

**Last documentation refresh:** 2026-10-21

This is the current health record. Historical wave narratives belong in Git,
`CHANGELOG.md`, or the archived status file; they do not override this page.

## Executive state

| Area | State | Evidence / limitation |
|---|---|---|
| Backend | Working prototype | FastAPI factory and route suite are active. |
| Frontend | Working prototype | React/Vite kiosk and clinician views build locally. |
| CardioVision | Working bounded slice | Deterministic mock plus optional local XGBoost assets; not clinical validation. |
| Intake | Working local flow | Voice/touch/UI flow and services exist; provider speech path is mocked. |
| OCR | Provider-capable boundary | LLM-backed path needs configured credentials; do not use real patient files locally. |
| Summary/FHIR | Local output | FHIR-shaped/minimal bundle; external validator and destination push are not proven. |
| ABDM | Local simulation | QR/webhook/SSE behavior is in-process; production gateway is not connected. |
| PM-JAY | Mock | No live NHA eligibility verification. |
| WhatsApp | Mock | No live Meta delivery or receipt verification. |
| Payments | Planned | No production payment gateway. |
| Hospital matcher | Narrow local referral | Cardiovascular candidates only; no verified marketplace/capacity. |
| Medical tourism | Planned | No treatment, travel, visa, or partner workflow. |
| Digital health passport | Planned | Consent/export concepts need a complete module. |
| Blender/3D | Planned | No active Blender asset pipeline in the runtime. |
| CI/CD | Syntax corrected; GitHub run pending | Existing workflow now has corrected indentation; hosted execution is still required before treating it as a merge gate. |
| Production readiness | Not ready | Security, provider, clinical, operational, and deployment evidence is incomplete. |

## Verified local baseline

Verification run on 2026-10-21 after this documentation refresh:

- backend tests: `290 passed`;
- Ruff checks: passed;
- strict mypy: passed;
- frontend production build: passed;
- launcher backend/frontend smoke: passed;
- CardioVision referral smoke: passed.

Frontend lint also exits 0 but reports existing non-blocking warnings in legacy large views/components. The CI workflow syntax was corrected in this refresh; GitHub execution remains the final CI verification.

## What is implemented

- Clean-architecture-shaped backend under `src/medikiosk/`.
- JWT role checks for core protected workflows.
- Session lifecycle, intake response handling, consent and purge behavior.
- Multilingual clinical question data and browser voice hooks.
- Document upload validation and OCR service boundary.
- Bilingual summary service and local FHIR-shaped persistence.
- Clinician queue, vitals/NEWS2, resource, standing-order, and audit flows.
- CardioVision screening and non-binding clinician-review referral endpoint.
- ABDM-shaped local QR, webhook, care-context, and SSE demo paths.
- Offline frontend fallbacks and IndexedDB/store-and-forward path.
- Docker backend image and Windows development launcher.

## Explicitly unverified or not live

- Production ABDM gateway, ABHA identity exchange, and FHIR push.
- Live PM-JAY/NHA eligibility.
- Live Meta WhatsApp delivery.
- Live Gemini/OpenAI usage with a governed PHI policy.
- Server-side multilingual ASR and measured medical-speech WER.
- Real OCR benchmark on a representative Indian medical-document corpus.
- CardioVision clinical calibration, subgroup performance, and `>90% AUC` evidence.
- Live hospital capacity, pricing, accreditation, travel, visa, or tourism data.
- Payment provider webhooks and reconciliation.
- Ambulance or emergency dispatch.
- Physical kiosk touchscreen, printer, camera, and edge-lockdown validation.
- Blender/GLB asset export and low-power 3D fallback.
- Production Redis wiring, migration rollout, observability, and incident drills.

## Current blockers

1. The target GitHub remote still needs to be configured and the baseline pushed.
2. Documentation formerly mixed historical completion claims with current status;
   this refresh is correcting that drift.
3. The CI workflow needs YAML parsing and execution verification before it is a
   trustworthy merge gate.
4. Legacy `server/`, `kiosk/`, `backend/`, and `core/` trees need an explicit
   disposition before large-scale refactoring.
5. External provider credentials and approved staging environments are absent.
6. The frontend still contains large views and inline styling that should be
   migrated incrementally to feature modules and a custom component system.

## Next recommended sequence

1. Commit and push the documentation spine.
2. Repair/verify CI and add security gates without claiming them early.
3. Classify legacy trees and record removals/migrations in an ADR.
4. Establish the custom shadcn-compatible design system and landing page.
5. Formalize CardioVision model registry, calibration, evaluation, and explainability.
6. Add reproducible Blender/GLB asset pipeline and 3D fallback.
7. Generalize screening and hospital/medical-tourism routing through ports.
8. Add sandbox adapters one by one with contract tests and evidence.
9. Add digital passport, follow-up, observability, and deployment operations.

## Delete zone / do not recreate

| Item | Reason | Replacement |
|---|---|---|
| New active code in `server/`, `kiosk/`, `backend/`, or `core/` | Parallel/legacy runtime creates drift | `src/medikiosk/` and `frontend/` |
| Claims that local ABDM/WhatsApp/PM-JAY mocks are live | Misrepresents external connectivity | `docs/INTEGRATIONS.md` status matrix |
| Hand-edited `docs/openapi.json` or `frontend/src/client/` | Generated contract drift | Export/generate scripts |
| Raw patient examples in docs/tests | PHI and privacy risk | Synthetic, redacted fixtures |
| New large route/view monoliths | Makes features hard to isolate and review | Ports/services/features/components |
