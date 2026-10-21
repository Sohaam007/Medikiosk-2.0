# MediKiosk 2.0

MediKiosk 2.0 is an extensible, privacy-aware health-journey platform for
Indian healthcare settings. Its product direction is:

```text
Screen → Intake → Explain → Route → Travel → Heal → Follow-up
```

The current repository is a reproducible working prototype centered on:

```text
CardioVision → multilingual intake → document capture → clinician queue
→ local summary/FHIR-shaped output → clinician-reviewed referral candidates
```

It is not a production clinical system. Several integrations are mocks or local
simulations. Read `docs/INTEGRATIONS.md` before describing a capability as live.

The project now uses a five-person delivery model: Soham (leader), Soumyadeep
(co-lead), Swapnil (ML/AI), Pabitra (QA/release), and Aditya
(integrations/synthetic data). The SEVA demo is intentionally frozen to a
reliable local vertical slice; the larger product roadmap continues separately.

## Start here

For a new coding session, read:

1. `AGENTS.md`
2. `docs/CONTEXT.md`
3. `docs/ARCHITECTURE.md`
4. `docs/STATUS.md`
5. `docs/INTEGRATIONS.md`
6. `docs/TESTS.md`
7. `docs/TEAM_CAPACITY.md`
8. `docs/SEVA_SUBMISSION.md`

For agent workflow, read `docs/AI_ORCHESTRATION.md`. For durable decisions,
read `docs/decisions/README.md` and the relevant ADR.

## Current stack

- Python `3.11.9`, FastAPI, Pydantic v2, SQLAlchemy, SQLite/PostgreSQL.
- `uv` with `uv.lock` for Python dependencies.
- Node `24.19.0`, React, TypeScript, Vite, Tailwind, and `package-lock.json`.
- Deterministic CardioVision mock mode and optional local XGBoost mode.
- Generated FastAPI OpenAPI contract and Hey-API TypeScript client.
- Docker runtime for the backend and Windows one-click local launcher.

## Setup

Prerequisites: Python `3.11.9`, `uv`, Node `24.19.0`, npm, and optionally
Docker.

```bash
uv sync --frozen --extra dev
cp .env.example .env                 # Linux/macOS
cd frontend && npm ci && cd ..
```

On Windows use `copy .env.example .env` or run the launcher, which reuses the
local environment and starts both processes.

## Run locally

### Windows one-click launcher

Double-click `start_dev.bat`, or run:

```powershell
.\start_dev.bat
.\start_dev.bat -NoBrowser
```

The launcher starts:

- backend: `http://127.0.0.1:8000`;
- frontend: `http://127.0.0.1:5173`.

It reuses responding services on those ports, waits for readiness, and opens the
frontend unless `-NoBrowser` is supplied. Stop it with `Ctrl+C` in both server
windows.

### Manual startup

Backend:

```bash
uv run uvicorn medikiosk.api.app:create_app --factory --reload --port 8000
```

Frontend in another terminal:

```bash
cd frontend
npm run dev
```

Vite proxies `/api` to `http://127.0.0.1:8000`; see `frontend/vite.config.ts`.

## Configuration modes

The offline demo uses:

```text
CARDIOVISION_MODE=mock
DATABASE_URL=sqlite+aiosqlite:///./medikiosk.db
```

`CARDIOVISION_MODE=real` loads the versioned local XGBoost assets. Gemini and
OpenAI adapters only make external calls when configured with credentials; do
not use real patient data in development.

## Verification

```bash
make test
uv run --extra dev ruff check src/ tests/
uv run --extra dev ruff format --check src/ tests/
uv run --extra dev mypy src/ --strict
cd frontend && npm run lint && npm run build
```

Run the focused checks in `docs/TESTS.md` for the area you changed. If an API
route or schema changes, export OpenAPI and regenerate the frontend client before
running the final checks.

## Active source map

| Need | Location |
|---|---|
| FastAPI app factory | `src/medikiosk/api/app.py` |
| API-to-adapter wiring | `src/medikiosk/api/dependencies/container.py` |
| Pure business rules | `src/medikiosk/domain/` |
| Ports/interfaces | `src/medikiosk/ports/` |
| Orchestration | `src/medikiosk/services/` |
| Infrastructure adapters | `src/medikiosk/adapters/` |
| Patient UI | `frontend/src/views/KioskIntakeView.tsx` |
| Clinician UI | `frontend/src/views/ClinicianQueueView.tsx` |
| CardioVision UI | `frontend/src/components/CardioVisionPanel.tsx` |
| API contract | `docs/openapi.json` |
| API client | `frontend/src/client/` |
| Tests | `tests/` |
| Model assets | `models/cardiovision/` |

`backend/`, `core/`, `server/`, and `kiosk/` are legacy/parallel surfaces. Do
not extend them without an explicit migration task.

## Safety and privacy

- CardioVision is screening support, not diagnosis.
- Do not log or commit PHI, secrets, raw audio, OCR text, or model payloads.
- Do not claim live ABDM, PM-JAY, WhatsApp, hospital, payment, ambulance, or
  medical-tourism integration from local mocks or UI cards.
- Do not deploy with the development secret, wildcard CORS, SQLite, or mock
  provider adapters.

## Documentation map

- `docs/CONTEXT.md` — product mission and vocabulary.
- `docs/ARCHITECTURE.md` — current architecture and file map.
- `docs/STATUS.md` — current verified state and blockers.
- `docs/INTEGRATIONS.md` — provider/mock boundaries.
- `docs/TESTS.md` — commands and test navigation.
- `docs/REGRESSION.md` — downstream verification map.
- `docs/ROADMAP.md` — sequenced production roadmap.
- `docs/TEAM_CAPACITY.md` — five-person ownership and parallel execution.
- `docs/SEVA_SUBMISSION.md` — frozen demo scope and submission claims.
- `docs/DEMO_EVIDENCE.md` — screenshots, recording, and verification evidence.
- `docs/CLINICAL_REGULATORY.md` — pilot-readiness and external review gates.
- `docs/AI_ORCHESTRATION.md` — agent task and handoff protocol.
- `docs/SECURITY.md` — implemented controls versus target controls.
- `docs/decisions/` — ADRs.

## Deployment note

The root `Dockerfile` runs the backend only. The frontend is built separately by
the Vite workflow. Production deployment requires managed secrets, a managed
database, approved CORS/TLS, real provider contracts, monitoring, clinical
governance, and an external security review.
