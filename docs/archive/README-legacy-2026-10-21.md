# MediKiosk 2.0 — SEVA 2026 working model

MediKiosk 2.0 is a reproducible, offline-ready health kiosk vertical slice for
the SEVA 2026 proposal. It combines the canonical MediKiosk clinical-intake
workflow with a bounded CardioVision cardiovascular screening engine:

**Screen → Intake → Explain → Route → Follow up**

The current demo lets a patient or community health worker:

1. open the Vite kiosk UI and choose a language;
2. run an explainable CardioVision heart-risk screen before clinical intake;
3. receive deterministic, non-binding cardiology candidate IDs for clinician
   review without selecting a doctor or purchasing a package;
4. continue through voice/touch intake, document capture, FHIR summary and
   the existing clinician queue; and
5. use the offline preview when the backend is unavailable.

The cardiovascular result is screening support only. It is not a diagnosis and
requires clinician review.

## Stack

- Python 3.11.9, FastAPI, Pydantic v2, SQLAlchemy, SQLite/PostgreSQL
- Vite, React 19, TypeScript, Tailwind CSS
- CardioVision model assets under `models/cardiovision/`
- FHIR R4/ABDM-oriented clinical contracts and an append-only audit trail
- `uv.lock` and `frontend/package-lock.json` for reproducible dependencies

## Setup

Prerequisites: Python 3.11.9, `uv`, Node 24.19.0 and npm.

```bash
uv sync --extra dev
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/macOS
cd frontend && npm ci && cd ..
```

No API key is required for the offline demo. Leave:

```text
CARDIOVISION_MODE=mock
```

To exercise the copied local XGBoost model assets explicitly, use
`CARDIOVISION_MODE=real`. This still does not call a remote service.

## Run

### One-click Windows startup

Double-click **`start_dev.bat`** in this folder. Keep `start_dev.ps1` next to it.
It starts the API and Vite in separate console windows, waits for both to respond,
then opens **http://127.0.0.1:5173**. Repeated launches reuse responding services
on ports 8000 and 5173; close other projects using these ports first.

The first launch installs locked dependencies if the local environment is absent
(internet required). It needs Python/uv and Node/npm installed, never overwrites
your `.env`, and never installs global packages. Existing environments are reused;
after dependency changes run `uv sync --frozen --extra dev` and `npm ci` manually.
For local demo authentication only, the example configuration contains a
development-only JWT secret. The launcher also supplies that value process-scoped
when `API_KEY` is blank; it never writes a secret to disk. Replace it before any
non-local deployment.
To stop the application, press **Ctrl+C in both server windows**.

For a readiness check without opening a browser:

```powershell
.\start_dev.bat -NoBrowser
```

This launches the local prototype, not a production deployment. The heart panel
still needs a configured demo JWT for backend referral requests; without one it
shows its labelled offline preview. Do not enter real patient data.

### Manual startup

Backend:

```bash
uv run uvicorn medikiosk.api.app:create_app --factory --reload --port 8000
```

Frontend in a second terminal:

```bash
cd frontend
npm run dev
```

Open the URL printed by Vite (normally `http://localhost:5173`). The kiosk
screen uses an offline preview if authentication or the API is not configured;
the API itself remains protected by the existing role-based dependency.

Useful API calls after configuring a valid kiosk JWT:

```bash
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/screening/cardiovascular \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MEDIKIOSK_JWT" \
  -d '{"features":{"Age":58,"HTN":1,"Typical Chest Pain":0}}'

curl -X POST http://localhost:8000/api/screening/cardiovascular/referral \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MEDIKIOSK_JWT" \
  -d '{"features":{"Age":72,"HTN":1,"Typical Chest Pain":1},"preferred_language":"hi-IN"}'
```

## Checks

The single offline project check is:

```bash
make test
```

It runs the complete Python suite, including architectural invariants and the
CardioVision boundary tests. Individual checks:

```bash
uv run --extra dev python -m pytest tests/ -q
uv run --extra dev ruff check src/ tests/
uv run --extra dev mypy src/ --strict
cd frontend && npm run build
```

## Deployment

Build and run the backend container:

```bash
docker build -t medikiosk-2-seva .
docker run --rm -p 8000:8000 medikiosk-2-seva
```

The container uses the pinned `uv` image, the lockfile, the factory entrypoint,
and the local SQLite default. Production deployments must provide a strong
secret, a managed database, TLS, an approved CORS allow-list, and a clinical
review process before enabling real patient traffic.

## Project guide

- `docs/archive/reference/medikiosk_2.0_vision-legacy.md` — SEVA product vision and phased plan
- `docs/archive/reference/seva_2026_recommendation-legacy.md` — category and problem-statement rationale
- `docs/SEVA_SUBMISSION.md` — implementation scope, demo script and submission checklist
- `docs/decisions/0008-cardiovision-boundary.md` — screening integration decision
- `models/cardiovision/` — copied, versioned CardioVision assets
- `frontend/src/components/CardioVisionPanel.tsx` — visible kiosk integration

## Privacy and clinical safety

Do not commit `.env`, real patient data, uploaded documents, database files,
tokens or API keys. Do not use the demo fixtures as clinical evidence. The
screening adapter does not log feature values, and the UI labels offline
results as previews.
