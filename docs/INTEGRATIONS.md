# MediKiosk 2.0 — Integration Truth

**Role:** canonical live-vs-mock integration matrix.

Use this file before implementing or describing an integration. “Present in the
UI” does not mean “connected to a provider.” A real integration needs a port,
adapter, configuration, contract tests, failure behavior, audit behavior, and
verified credentials in an approved environment.

## Status vocabulary

- **Local:** implemented inside this repository; no provider call.
- **Mock:** deterministic or simulated adapter for development/tests.
- **Provider-capable:** a provider adapter exists and can call externally when
  configured, but live credentials or end-to-end evidence are not part of the
  local baseline.
- **Sandbox pending:** the port and adapter seam are ready, but a provider
  sandbox verification is still required.
- **Planned:** product intent or UI/domain groundwork exists; no complete
  integration is active.
- **Verified live:** only use this label when a dated, reproducible test proves
  the external flow with approved credentials.

## Current integration matrix

| Capability | Current implementation | Status | External egress now? | Next safe step |
|---|---|---|---:|---|
| FastAPI API | `src/medikiosk/api/app.py` | Local | No | Keep routes thin and contract-tested. |
| SQLite persistence | SQLAlchemy repositories under `src/medikiosk/adapters/database/` | Local | No | Add migration-first production database workflow. |
| PostgreSQL | `DATABASE_URL` supports `asyncpg` | Provider-capable | No in local default | Verify migrations and pool behavior in a disposable environment. |
| Cache | `InMemoryCacheAdapter` is wired by the container | Local | No | Add a real Redis adapter and select it only when explicitly configured. |
| Gemini | `src/medikiosk/adapters/llm/gemini.py` | Provider-capable | Yes when key/configured | Add consent/egress policy, staging key, redacted telemetry, and live contract test. |
| OpenAI | `src/medikiosk/adapters/llm/openai_adapter.py` | Provider-capable | Yes when key/configured | Same egress and staging controls as Gemini. |
| Speech transcription | `src/medikiosk/api/routes/speech.py` returns language-specific mock text | Mock | No | Introduce an `ASRPort`, local provider option, and accuracy evaluation. |
| Document OCR | `OCRService` plus configured LLM adapter | Provider-capable | Depends on LLM settings | Add explicit OCR port, provider selection, redaction policy, and fixture benchmark. |
| CardioVision mock | `CardioVisionAdapter(mode="mock")` | Local | No | Keep deterministic regression tests. |
| CardioVision real | Local XGBoost assets under `models/cardiovision/` | Local | No | Add model card, calibration report, subgroup evaluation, and model registry. |
| CardioVision referral | Pure matcher plus local doctor/package repositories | Local/mock | No | Generalize to verified hospital routing without automatic booking. |
| ABDM QR/webhook/SSE | `src/medikiosk/api/routes/abdm.py` | Local/mock | No | Add signed sandbox gateway adapter and route authentication policy. |
| ABDM FHIR push | `MockABDMGateway` exists but is not the active route composition | Mock | No | Wire a port through a service, then add a sandbox adapter. |
| PM-JAY | `MockPMJAYAdapter` | Mock | No | Add official sandbox contract and credential boundary. |
| WhatsApp | `MockWhatsAppNotificationAdapter` | Mock | No | Add Meta adapter, templates, opt-in, delivery receipts, and retry policy. |
| Payments/UPI | Domain/UI groundwork only | Planned | No | Add `PaymentGatewayPort`, mock transaction lifecycle, webhook verification, and emergency bypass. |
| Hospital/EHR | FHIR-shaped local output and UI cards | Planned/local | No | Add destination-specific FHIR validation and an authenticated partner adapter. |
| Medical tourism | Narrow cardiology candidate matching only | Planned/local | No | Add hospital, treatment, budget, travel, visa, and availability contracts. |
| Ambulance/emergency dispatch | UI/domain concepts only | Planned | No | Add a verified dispatch provider and a clinical safety gate. |
| Digital health passport | Not a complete active module | Planned | No | Define consent, expiry, revocation, export, and audit contracts first. |
| AI follow-up | Not implemented as a complete workflow | Planned | No | Define care-plan, consent, message, delivery, and escalation contracts. |
| Blender/3D assets | No active Blender pipeline in repository runtime | Planned | No | Add reproducible `.blend`/GLB export and low-power fallback. |

## Known external-data boundaries

The following code can send data outside the local process when configured:

- Gemini adapter calls the Google GenAI SDK.
- OpenAI adapter calls the OpenAI SDK.
- Any future real adapter under `src/medikiosk/adapters/` must be treated as
  external egress until reviewed.

The following are currently local simulations and do not prove provider access:

- ABDM webhook and SSE events;
- PM-JAY eligibility;
- WhatsApp paging;
- CardioVision real mode (local model assets);
- browser speech route;
- doctor/package availability;
- hospital capacity and referral candidates.

## Route/auth caution

Do not assume every `/api` route has the same authentication policy. The
currently public or locally simulated surfaces include `/api/health`, token
issuance under `/api/auth/token`, the speech route, and portions of the ABDM
QR/webhook/SSE flow. Core intake, clinician, document, summary, and screening
routes use explicit auth dependencies. Verify decorators in the route file and
`src/medikiosk/api/dependencies/auth.py` before adding a client call.

## Adapter implementation checklist

For every new provider:

1. Define or reuse a domain contract.
2. Define a narrow `typing.Protocol` in `src/medikiosk/ports/`.
3. Implement a deterministic mock adapter first.
4. Add provider configuration as secret-safe settings.
5. Add a real/sandbox adapter without importing it into domain code.
6. Add timeout, retry, idempotency, rate-limit, and failure semantics.
7. Define what is logged; never log raw PHI or provider payloads.
8. Add contract tests against the mock and sandbox tests where credentials exist.
9. Expose health/readiness without exposing credentials or patient data.
10. Update this document, `docs/STATUS.md`, and the relevant ADR.

## Promotion gates

An integration may move from Mock to Sandbox only when its request/response
contract, error mapping, auth, audit, and test fixture are committed. It may
move from Sandbox to Verified live only with a dated evidence record, approved
credentials, provider delivery/readback proof, monitoring, and rollback steps.
