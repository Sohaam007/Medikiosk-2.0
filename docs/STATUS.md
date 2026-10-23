# MediKiosk 2.0 — Current Status

**Last status refresh:** 2026-10-23

This page records the current verified state. Historical wave narratives belong
in Git history or an ignored local area outside the repository; they do not
override this page.

## Executive state

| Area | State | Evidence / limitation |
|---|---|---|
| Backend | Working prototype | FastAPI factory and route suite are active. |
| Frontend | Working prototype | React/Vite kiosk and clinician views build locally. |
| Team | Five-person delivery model | Soham leader; Soumyadeep co-lead; Swapnil ML; Pabitra QA/release; Aditya integrations/data. |
| SEVA scope | Frozen local demo track | CardioVision → intake → clinician handoff; no live provider claims. |
| CardioVision | Working bounded slice | Deterministic mock plus optional local XGBoost assets; not clinical validation. |
| Intake | Working local flow | Voice/touch/UI flow exists; provider speech path is mocked. |
| OCR | Provider-capable boundary | LLM-backed path needs configured credentials; no real patient files. |
| Summary/FHIR | Local output | FHIR-shaped/minimal bundle; external validator/destination push unproven. |
| ABDM | Local simulation | QR/webhook/SSE behavior is in-process; production gateway not connected. |
| PM-JAY | Mock | No live NHA eligibility verification. |
| WhatsApp | Mock | No live Meta delivery/readback. |
| Product-scale roadmap | Planned | Multi-disease, passport, routing, integrations, 3D, and operations are Track B. |
| CI/CD | Hosted PR checks passing | Backend, frontend, repository hygiene, and quality-gate checks passed on PR #1; `main` is protected. |
| Production readiness | Not ready | Clinical, regulatory, provider, operational, and deployment evidence incomplete. |

## Verified local baseline

Verification run on October 22, 2026 after the five-person plan refresh:

- backend tests: `290 passed`;
- Ruff check/format: passed;
- strict mypy: passed;
- frontend lint: exit 0 with existing non-blocking warnings;
- frontend production build: passed;
- launcher/backend/frontend smoke: passed;
- CardioVision referral smoke: passed;
- repository hygiene: passed;
- hosted PR #1 CI: backend, frontend, hygiene, and quality gate passed;
- documentation governance audit: passed;
- main branch baseline is pushed to `https://github.com/Sohaam007/Medikiosk-2.0`;
- governance changes are on PR #1 and are not merged into `main` yet.

## Current blockers and evidence gaps

1. Dated screenshots and a screen recording are still required for the SEVA
   submission package.
2. PR #1 still requires human code-owner review and merge; agents must not merge it.
3. The four legacy code trees need an explicit disposition before a large
   refactor; new active work must not enter them.
4. CardioVision evaluation methodology exists in the plan, but no clinical
   validation or `>90% AUC` evidence is available.
5. Regulatory classification and intended-use review require qualified external
   clinical/regulatory input before pilot use.
6. Provider credentials, sandbox environments, and a pilot hospital/clinical
   reviewer are not available in the local repository.

## Next sequence

### SEVA Demo Track

1. Soham freezes claims and acceptance criteria.
2. Soumyadeep and Aditya harden the repeatable kiosk-to-clinician flow.
3. Swapnil produces the CardioVision evidence pack.
4. Pabitra runs regression/release gates and captures evidence.
5. The full team reviews the submission package and records unresolved gaps.

### Product Scale Track

1. Clinical/regulatory readiness and screening registry.
2. Custom design system, landing page, and community screening mode.
3. Model evaluation, multi-disease slots, and optional Blender/3D.
4. ABDM/FHIR/PM-JAY/communications/provider routing adapters.
5. Digital passport, follow-up, observability, and production operations.

## Delete zone / do not recreate

| Item | Reason | Replacement |
|---|---|---|
| New active code in `server/`, `kiosk/`, `backend/`, or `core/` | Parallel runtime creates drift | `src/medikiosk/` and `frontend/` |
| Claims that local mocks are live | Misrepresents external connectivity | `docs/INTEGRATIONS.md` and `docs/SEVA_SUBMISSION.md` |
| Hand-edited OpenAPI/generated client | Contract drift | Export/generate scripts |
| Raw patient examples | PHI/privacy risk | Synthetic fixtures |
| Full product features added to the demo freeze | Destabilizes submission | Track B roadmap/task packet |

## 2026-10-23 documentation refresh

The Product Scale Track now has a documented separation between clinical
screening models, deterministic safety policy, the bounded AI assistant, and the
Blender/GLB explanation layer:

- canonical design: `docs/3D_AND_ASSISTANT_ARCHITECTURE.md`;
- asset workflow and generation policy: `docs/BLENDER_PIPELINE.md`;
- model/assistant governance: `docs/MODEL_GOVERNANCE.md`;
- durable decision draft: ADR 0013;
- feature register: F-008 and F-009;
- regression coverage expectations: `docs/REGRESSION.md`.

The selected clinical-asset approach is deterministic Blender Python assembly
from licensed, clinician-reviewed reference geometry. Optional Hunyuan3D-2 use
is limited to local, non-clinical blockouts and is not a runtime dependency.
The 3D runtime, GLB exports, scene registry, and assistant contract are still
unimplemented; the SEVA demo remains valid without them.
