# Frontend Handoff — Current Runtime

The active frontend is `frontend/`, a React 19 + TypeScript + Vite application.
It is not a Next.js application.

## Run

```bash
cd frontend
npm ci
npm run dev
```

Node is pinned to `24.19.0` in the root `.nvmrc`. Vite serves port `5173` and
proxies `/api` to `http://127.0.0.1:8000`.

## Active views

- `src/views/KioskIntakeView.tsx`: patient/proxy kiosk workflow.
- `src/views/ClinicianQueueView.tsx`: clinician queue and review workflow.
- `src/components/CardioVisionPanel.tsx`: current screening/referral surface.

## API client

The backend OpenAPI schema is exported from the FastAPI app and then used to
generate `src/client/`:

```bash
uv run --extra dev python scripts/export_openapi.py
cd frontend && npm run generate-client
```

Use generated functions/types. Do not hand-edit generated files or create a
second handwritten contract.

## Authentication caution

Authentication is route-specific. Inspect the backend route decorator and
`src/medikiosk/api/dependencies/auth.py` before using a raw `fetch`. The local
UI may fall back to offline/demo state when auth or the API is unavailable; label
that state and never show a fake provider success.

## Required checks

```bash
npm run lint
npm run build
```

For API changes also run OpenAPI export, SDK generation, backend tests, and the
full regression row in `docs/REGRESSION.md`.
