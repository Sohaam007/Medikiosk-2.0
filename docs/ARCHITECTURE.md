# MediKiosk 2.0 — Current Architecture Map

**Role:** canonical map of the active repository. This document describes the
runtime that exists now and the boundaries future features must use.

## Runtime boundary

There is one active backend runtime and one active frontend runtime.

```text
Browser / kiosk
      │
      ▼
frontend/ (React 19 + TypeScript + Vite)
      │  /api proxy during development
      ▼
src/medikiosk/api/app.py:create_app
      │
      ├── API routes and request/response schemas
      ├── dependency composition boundary
      ├── application services
      ├── domain contracts and pure policies
      └── infrastructure adapters
```

### Active entrypoints

| Concern | Entry point |
|---|---|
| Backend ASGI app | `medikiosk.api.app:create_app` |
| Backend local command | `uv run uvicorn medikiosk.api.app:create_app --factory --reload --port 8000` |
| Frontend dev command | `cd frontend && npm run dev` |
| Windows launcher | `start_dev.bat` → `start_dev.ps1` |
| Frontend proxy | `frontend/vite.config.ts` (`/api` → `127.0.0.1:8000`) |
| API schema export | `scripts/export_openapi.py` → `docs/openapi.json` |
| Frontend SDK generation | `frontend` `npm run generate-client` → `frontend/src/client/` |
| Container entrypoint | root `Dockerfile` → Uvicorn on port 8000 |

## Active package layout

```text
src/medikiosk/
├── domain/                         pure clinical and business rules
│   ├── contracts/                  Pydantic models crossing boundaries
│   ├── intake/                     clinical question and language logic
│   ├── triage/                     risk, NEWS2, veto, and red flags
│   ├── ocr/                        document-domain types and policies
│   ├── synthesis/                  summary-domain types
│   ├── fhir/                       FHIR-domain types
│   ├── consent/                    consent-domain boundary
│   ├── timeline/                   clinical event ordering
│   ├── screening/                  screening policies and future registry
│   ├── referral_matcher.py         current CardioVision candidate policy
│   ├── resource_allocator.py       clinical resource rules
│   ├── standing_orders.py          standing-order rules
│   └── pharma_safety.py            medication-safety rules
├── ports/                          provider and repository protocols
├── services/                       use-case orchestration
├── adapters/                       persistence, model, storage, and mock adapters
└── api/
    ├── app.py                      FastAPI factory and router registration
    ├── dependencies/container.py   composition root for current API
    ├── dependencies/auth.py        JWT role checks
    ├── routes/                     thin HTTP route handlers
    ├── schemas/                    API-specific Pydantic shapes
    └── middleware/                 API middleware surface
```

## Dependency direction

```text
api ───────► services ───────► ports ───────► domain
  │              │               ▲
  └──────────────┴───────────────┘
                 adapters implement ports
```

Rules:

- `src/medikiosk/domain/` never imports `src/medikiosk/api/`,
  `src/medikiosk/services/`, or `src/medikiosk/adapters/`.
- `src/medikiosk/domain/` does not read environment variables, files, network responses,
  databases, wall-clock time, random state, or model SDKs.
- `src/medikiosk/ports/` expresses capabilities without provider-specific types.
- `src/medikiosk/services/` owns workflow sequencing, persistence calls, and adapter use.
- `src/medikiosk/api/` owns HTTP concerns only; routes should not contain clinical policy.
- `src/medikiosk/api/dependencies/container.py` is the current adapter wiring chokepoint.
- New modules must follow the same direction even before a future bootstrap
  package is introduced.

## Current service wiring

`src/medikiosk/api/dependencies/container.py` currently provides:

- SQLAlchemy session and repository dependencies;
- Gemini or OpenAI LLM selection from settings;
- local filesystem storage;
- in-memory cache fallback;
- local doctor and package catalogs;
- mock PM-JAY eligibility;
- mock WhatsApp notifications;
- CardioVision mock or local-model adapter;
- intake, OCR, session, and summary services.

When adding an adapter, wire it here only after its port, configuration, mock,
tests, and failure policy exist.

## API route groups

| Route group | Responsibility |
|---|---|
| health | process/health probe |
| auth | development JWT issuance and auth support |
| intake and session | session lifecycle, responses, vitals, sync, billing-related intake actions |
| screening | CardioVision screening and referral candidates |
| documents | upload, OCR processing, session document listing |
| speech | current deterministic speech boundary |
| summary and fhir | summary and locally persisted FHIR-shaped output |
| clinician | queue, session detail, paging, clinician actions |
| doctors and packages | local catalog data |
| abdm | local QR/webhook/SSE simulation and care-context-shaped flow |
| resources | local clinical resource allocation |
| analytics | surge-radar and operational metrics |
| audit | audit verification/readback |

The exact contract is `docs/openapi.json`, generated from the running FastAPI
application. Route decorators and auth dependencies are the authority for
authentication; do not infer auth from the route prefix.

## End-to-end data flow

```text
Language/informant selection
        ↓
SessionService creates opaque session UUID
        ↓
CardioVision screening (optional, mock or local model)
        ↓
Voice/touch responses → IntakeService → triage/veto policy
        ↓
Documents → storage → OCRService → LLM adapter or test adapter
        ↓
Session + intake + documents → SummaryService
        ↓
Bilingual summary + minimal local FHIR-shaped bundle
        ↓
Clinician queue and local referral candidates
        ↓
Consent-gated purge / audit trail
```

The current summary path does not prove external FHIR validation or ABDM
transmission. Keep those as separate adapter capabilities.

## Frontend boundaries

The current frontend is a two-mode application switched from `App.tsx`:

```text
App
├── NanoBanner + mode navigation
├── KioskIntakeView
│   ├── language and informant selection
│   ├── intake conversation and voice hooks
│   ├── ABDM local QR/SSE flow
│   ├── CardioVisionPanel
│   ├── document scanner
│   ├── doctor/package selection
│   └── token/wayfinding/receipt flow
└── ClinicianQueueView
    ├── queue and triage
    ├── patient/session detail
    ├── documents and FHIR download
    ├── integrations presentation
    └── surge/resource/standing-order tools
```

Future UI work should move capability-specific behavior into feature folders under
`frontend/src/` and shared primitives into the existing `frontend/src/components/`
tree rather than growing the two large views indefinitely. The migration must
preserve behavior with tests.

## Generated contracts

The backend contract flow is:

```text
FastAPI route/schema
  → scripts/export_openapi.py
  → docs/openapi.json
  → frontend npm run generate-client
  → frontend/src/client/{sdk,types}.gen.ts
```

Generated files are committed outputs. Do not hand-edit them. A route/schema
change is incomplete until the export, client generation, backend checks, and
frontend build all pass.

## Data and persistence

- Local default: SQLite via `sqlite+aiosqlite`.
- Production direction: PostgreSQL via `asyncpg`.
- Repositories: `src/medikiosk/adapters/database/`.
- Local storage: `LocalStorageAdapter` under the configured storage path.
- Cache currently wired: in-memory; Redis configuration exists but is not the
  active dependency implementation.
- Database startup creates tables for local development; production must use a
  migration-controlled lifecycle.

## Active versus legacy trees

| Tree | Status | Rule |
|---|---|---|
| `src/medikiosk/` | Active | All new backend runtime work goes here. |
| `frontend/` | Active | All new browser UI work goes here. |
| `tests/` | Active | Add regression and contract evidence here. |
| `models/cardiovision/` | Active local model assets | Version/model-card changes require evaluation evidence. |
| `server/` | Legacy/parallel | Read only for migration context; do not extend by default. |
| `kiosk/` | Legacy/parallel | Do not treat as the active kiosk UI. |
| `backend/` | Legacy/parallel/deployment remnants | Do not add runtime code without a migration task. |
| `core/` | Legacy/parallel | Not packaged by `pyproject.toml`; do not use as active source. |

## Planned extensibility seams

The product roadmap will add capabilities through these seams:

- `ScreeningModelPort` for cardiovascular, cognitive, metabolic, respiratory,
  and multi-disease models.
- `HospitalMatcherPort` and `MedicalTourismPort` for routing.
- `ASRPort`, `OCRPort`, and `FollowupPort` for provider-independent workflows.
- `ABDMGateway`, `FHIRDestinationPort`, `PaymentGatewayPort`, and
  `CommunicationsPort` for external systems.
- `ModelRegistryPort` for version, calibration, and rollback metadata.
- Blender export manifests plus GLB/Three.js components for 3D explanation.

Every seam starts with a deterministic mock and a contract test.
