# MediKiosk 2.0 — Agent Constitution

This file is the active instruction surface for coding agents. Read it before
editing anything. The linked documents are context and navigation; verify their
claims against current code, configuration, tests, and Git history before acting.

## First-session reading order

Read only this sequence first; it is designed to preserve context:

1. `docs/CONTEXT.md` — product mission, vocabulary, safety boundaries.
2. `docs/ARCHITECTURE.md` — active runtime, package map, dependency direction.
3. `docs/STATUS.md` — verified current state, blockers, and limitations.
4. `docs/INTEGRATIONS.md` — live, mock, local, and unimplemented integrations.
5. `docs/TESTS.md` — exact commands and focused verification.
6. `docs/TEAM_CAPACITY.md` — five-person ownership and parallel workstreams.
7. `docs/SEVA_SUBMISSION.md` — frozen demo scope and claim boundaries.
8. Task-specific ADRs in `docs/decisions/`.

After this first-session sequence, read `docs/FEATURES.md` and
`docs/tasks/active/README.md` before starting non-trivial implementation work.

Do not read the entire historical `docs/tasks/` directory to choose work. It
contains older planning material and is not a reliable current backlog.

## Current product truth

MediKiosk 2.0 is an offline-first clinical-intake prototype with a CardioVision
screening vertical slice. The active journey is:

```text
Screen → Intake → Explain → Route → Follow up
```

The wider product target is:

```text
Screen → Intake → Explain → Route → Travel → Heal → Follow-up
```

The current repository is not a production clinical system. ABDM, PM-JAY,
WhatsApp, hospital/EHR, payment, ambulance, medical-tourism, and live-capacity
connections are not proven live integrations. See `docs/INTEGRATIONS.md`.

The five-person delivery model is: Soham (leader), Soumyadeep (co-lead), Swapnil
(ML/AI), Pabitra (QA/release), and Aditya (integrations/synthetic data). See
`docs/team/` for role-specific instructions.

## Active runtime and source of truth

- Backend package: `src/medikiosk/`.
- FastAPI factory: `src/medikiosk/api/app.py` (`create_app`).
- Dependency/composition boundary: `src/medikiosk/api/dependencies/container.py`.
- Frontend: `frontend/`, React + TypeScript + Vite.
- Patient workflow: `frontend/src/views/KioskIntakeView.tsx`.
- Clinician workflow: `frontend/src/views/ClinicianQueueView.tsx`.
- Generated HTTP contract: `docs/openapi.json`.
- Generated TypeScript client: `frontend/src/client/`.
- CardioVision assets: `models/cardiovision/`.
- Local launcher: `start_dev.bat` and `start_dev.ps1`.

The directories `backend/`, `core/`, `server/`, and `kiosk/` contain legacy or
parallel implementation surfaces. Do not add new active runtime code there
unless a task explicitly migrates one and includes a removal plan.

## Architecture rules

The dependency direction is inward:

```text
api → services → ports → domain
adapters → ports and domain contracts
```

- `src/medikiosk/domain/` is deterministic business logic: no filesystem, network, database,
  environment access, wall-clock reads, or model SDK imports.
- `src/medikiosk/ports/` contains capability interfaces and stable contracts.
- `src/medikiosk/services/` orchestrates use cases and coordinates repositories/adapters.
- `src/medikiosk/adapters/` implements external systems, persistence, model loading, and
  provider-specific behavior.
- `src/medikiosk/api/` stays thin: validate, authorize, call a service/port, map responses.
- `src/medikiosk/api/dependencies/container.py` is currently the intended API-to-adapter
  wiring boundary.
- Reuse contracts in `src/medikiosk/domain/contracts/`; widening a required
  field requires an ADR first.

## Clinical and privacy non-negotiables

- Screening is not diagnosis; every screening response retains clinician review.
- A critical clinical veto bypasses doctor choice, packages, payment, and routine
  queue routing.
- Never log names, ABHA IDs, Aadhaar numbers, phone numbers, diagnoses,
  medications, lab values, transcripts, OCR text, audio, or raw model output.
  Log opaque session IDs and operational metadata only.
- Never put secrets in source, committed `.env` files, fixtures, screenshots,
  documentation, or example payloads. `.env` is local and ignored.
- Gemini/OpenAI are external PHI egress when configured; do not call the app
  fully offline when those adapters are enabled.
- Validate upload MIME type, size, and empty input before processing.
- Catch specific exceptions; do not add broad swallowing or silent fallbacks that
  make an unauthorized backend call look successful.

## Setup and exact commands

Pinned runtimes are `.python-version` (`3.11.9`) and `.nvmrc` (`24.19.0`).

```bash
uv sync --frozen --extra dev
cd frontend && npm ci && cd ..
```

Windows one-click startup:

```powershell
.\start_dev.bat
.\start_dev.bat -NoBrowser
```

Manual startup:

```bash
uv run uvicorn medikiosk.api.app:create_app --factory --reload --port 8000
cd frontend && npm run dev
```

Authoritative local checks:

```bash
make test
uv run --extra dev ruff check src/ tests/
uv run --extra dev ruff format --check src/ tests/
uv run --extra dev mypy src/ --strict
cd frontend && npm run lint && npm run build
python scripts/check_repo_hygiene.py
```

On Windows without `make`, run the `uv` and `npm` commands directly. Run the
full Python suite after backend, contract, adapter, or generated-client changes;
run frontend lint/build after frontend or OpenAPI changes.

## Generated artifacts and API changes

When routes or Pydantic schemas change, execute in this order:

```bash
uv run --extra dev python scripts/export_openapi.py
cd frontend && npm run generate-client
cd ..
uv run --extra dev ruff check src/ tests/
uv run --extra dev mypy src/ --strict
uv run --extra dev python -m pytest tests/ -q
cd frontend && npm run build
```

Do not hand-edit `docs/openapi.json` or generated files under
`frontend/src/client/`. If the generated diff is unexpectedly large, stop and
inspect the OpenAPI change before committing.

## Feature delivery protocol

Every non-trivial feature needs a bounded task packet containing the user
outcome, allowed/forbidden paths, contract/port changes, mock behavior, external
egress implications, tests, rollback plan, and documentation owner.

Implement in this order unless an ADR justifies another order:

```text
contract → port → mock adapter → domain/service → API → generated client → UI
→ focused tests → full checks → docs/status update
```

Use one branch and one logical commit per capability. Follow
`docs/WORKFLOW.md` and `docs/AI_ORCHESTRATION.md`.

## Pull-request-only delivery

- Never commit directly on `main` or `master`.
- Never push directly to `main` or `master`.
- If the current branch is `main` or `master`, create a task branch before editing.
- Agents may push only their task branch and may open or update a pull request.
- Agents must not merge pull requests; a human owner merges after required review
  and required checks pass.
- Before pushing a task branch, inspect `git status`, `git diff`,
  `git diff --check`, and the staged file list. Stage only files allowed by the
  task packet.
- A pull request must link its feature ID/task packet and record exact checks.
- GitHub branch protection is the enforcement layer; local instructions alone are
  not considered sufficient.

## Documentation governance

- `AGENTS.md` is the constitution and must stay short enough to read every
  session.
- `docs/ARCHITECTURE.md` is the current map, not a historical narrative.
- `docs/STATUS.md` is the current health/blocker record.
- `docs/TEAM_CAPACITY.md` owns team lanes and delivery capacity.
- `docs/SEVA_SUBMISSION.md` owns the frozen competition/demo scope.
- `docs/FEATURES.md` owns the active feature index and feature status links.
- `docs/tasks/active/` owns bounded implementation packets; historical
  `docs/tasks/` files are not the active backlog.
- `docs/INTEGRATIONS.md` owns live-vs-mock integration truth.
- `docs/TESTS.md` owns executable verification guidance.
- `docs/DEMO_EVIDENCE.md` owns screenshots, recording, and submission evidence.
- `docs/CLINICAL_REGULATORY.md` owns pilot-readiness and regulatory discovery.
- `docs/decisions/` owns durable architectural decisions.
- Update the canonical owner when its fact changes; do not duplicate changing
  facts into several documents.

## Stop conditions

Stop and ask for a decision, or record an ADR, when:

- a cross-module contract is widened;
- a dependency, provider, database, model, or deployment target is added;
- patient data may leave the process or cross a trust boundary;
- a legacy directory would become active again;
- tests and documentation disagree;
- a production claim would rely only on a mock or UI card.
