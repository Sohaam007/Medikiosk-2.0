# MediKiosk 2.0 — Verification Guide

**Role:** executable checks and test navigation.

Run the smallest focused check while iterating, then run the complete relevant
gate before declaring work complete. Documentation is not evidence; command
output is evidence.

## Runtime setup

Pinned runtimes:

- Python: `.python-version` → `3.11.9`.
- Node: `.nvmrc` → `24.19.0`.
- Python lockfile: `uv.lock`.
- Frontend lockfile: `frontend/package-lock.json`.

```bash
uv sync --frozen --extra dev
cd frontend && npm ci && cd ..
```

## Authoritative checks

### Full backend suite

```bash
uv run --extra dev python -m pytest tests/ -q
```

`make test` is the project shortcut for the same suite on systems with Make.

### Backend quality

```bash
uv run --extra dev ruff check src/ tests/
uv run --extra dev ruff format --check src/ tests/
uv run --extra dev mypy src/ --strict
```

### Frontend quality

```bash
cd frontend
npm run lint
npm run build
```

### API/client synchronization

Run after route or schema changes:

```bash
uv run --extra dev python scripts/export_openapi.py
cd frontend
npm run generate-client
npm run build
```

The generated OpenAPI file and client must be committed together with the
source change. Never hand-edit generated files.

## Focused checks

| Change | First check | Then run |
|---|---|---|
| Domain rule or contract | `uv run --extra dev python -m pytest tests/unit/domain -q` | Full backend suite, invariants, mypy. |
| CardioVision | `uv run --extra dev python -m pytest tests/unit/adapters/test_cardiovision_adapter.py tests/unit/domain/test_referral_matcher.py tests/e2e/test_screening_api.py -q` | Full backend suite and model evaluation when model behavior changes. |
| Intake/session | `uv run --extra dev python -m pytest tests/e2e/test_intake_api.py tests/integration/test_e2e_stack_flow.py -q` | Full backend suite. |
| Speech | `uv run --extra dev python -m pytest tests/unit/test_speech_api.py tests/e2e/test_speech_api.py -q` | Full backend suite. |
| Documents/OCR | `uv run --extra dev python -m pytest tests/e2e/test_document_api.py tests/integration/test_adapters.py -q` | Full backend suite; never use real patient files. |
| ABDM simulation | `uv run --extra dev python -m pytest tests/unit/test_abdm_api.py tests/e2e/test_abdm_api.py -q` | Full backend suite and integration boundary review. |
| PM-JAY/communications | `uv run --extra dev python -m pytest tests/e2e/test_pmjay_comms_api.py -q` | Full backend suite. |
| Clinician queue/resources | `uv run --extra dev python -m pytest tests/e2e/test_clinician_api.py tests/e2e/test_phase3_routes.py tests/e2e/test_expansion_waves.py -q` | Full backend suite. |
| Summary/FHIR | `uv run --extra dev python -m pytest tests/e2e/test_summary_api.py -q` | Full backend suite and inspect FHIR validation claims. |
| Frontend component/style | `cd frontend && npm run lint && npm run build` | Browser/accessibility checks when available. |

## Test categories

- `tests/unit/domain/`: pure business logic; no network or database.
- `tests/unit/adapters/`: adapter behavior with deterministic fixtures.
- `tests/integration/`: services/adapters and full local stack boundaries.
- `tests/e2e/`: FastAPI workflow behavior.
- `tests/invariants/`: import direction, domain purity, safety chokepoints, and
  audit guarantees.

## Test discipline

- Use synthetic fixtures only.
- Every bug fix adds a regression test before or with the fix.
- Contract changes require endpoint and generated-client checks.
- Mock tests prove local behavior, not provider connectivity.
- A passing frontend build does not prove API authorization or external delivery.
- A passing model test does not prove clinical performance; use `eval/` reports
  for AUC, calibration, subgroup, and threshold evidence.

## Local smoke test

With the backend and frontend running:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/api/health
Invoke-WebRequest http://127.0.0.1:5173
```

The referral smoke path requires a development JWT. Use the existing auth token
route and the example payloads in `README.md`; never paste real patient data.

## Evidence to record

For each completed feature record:

- exact command;
- exit code and meaningful summary;
- environment/mode (`mock`, `real`, sandbox, or production);
- test fixture class (synthetic only);
- generated artifacts changed;
- known gap or unverified external dependency.
