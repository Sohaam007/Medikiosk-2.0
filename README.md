# MediKiosk 2.0 — SEVA 2026 working model

MediKiosk 2.0 is a reproducible, offline-ready health kiosk vertical slice for
the SEVA 2026 proposal. It combines the canonical MediKiosk clinical-intake
workflow with a bounded CardioVision cardiovascular screening engine:

**Screen → Intake → Explain → Route → Follow up**

The current demo lets a patient or community health worker:

1. open the Vite kiosk UI and choose a language;
2. run an explainable CardioVision heart-risk screen before clinical intake;
3. continue through voice/touch intake, document capture, FHIR summary and
   the existing clinician queue; and
4. use the offline preview when the backend is unavailable.

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

- `medikiosk_2.0_vision.md` — SEVA product vision and phased plan
- `seva_2026_recommendation.md` — category and problem-statement rationale
- `docs/SEVA_SUBMISSION.md` — implementation scope, demo script and submission checklist
- `docs/decisions/0008-cardiovision-boundary.md` — screening integration decision
- `models/cardiovision/` — copied, versioned CardioVision assets
- `frontend/src/components/CardioVisionPanel.tsx` — visible kiosk integration

## Privacy and clinical safety

Do not commit `.env`, real patient data, uploaded documents, database files,
tokens or API keys. Do not use the demo fixtures as clinical evidence. The
screening adapter does not log feature values, and the UI labels offline
results as previews.
