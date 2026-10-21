# MediKiosk 2.0 — AI Agent Operating Model

**Role:** repeatable workflow for OpenCode, Claude, Codex, Copilot, Gemini, and
other coding agents working on this repository.

The project uses AI for implementation, but no agent is allowed to turn an
unverified prototype into a production claim. Agents must produce small,
reviewable, executable changes with evidence.

## Agent session contract

Every implementation session starts by reading:

```text
AGENTS.md
docs/CONTEXT.md
docs/ARCHITECTURE.md
docs/STATUS.md
docs/INTEGRATIONS.md
docs/TESTS.md
```

Then read only the task-specific files and relevant ADRs. Do not load the whole
repository or every historical task file by default.

## Task packet

No agent should receive an unbounded request such as “improve the app.” Use this
packet for every feature, fix, migration, model, integration, or UI change:

```markdown
# Task: <short name>

## User outcome
<What becomes possible or safer?>

## Scope
- Allowed paths:
- Forbidden paths:
- Out of scope:

## Current evidence
- Existing entrypoints:
- Existing contracts/ports:
- Existing tests:
- Relevant ADRs:

## Contract
- Request/response or domain shape:
- Auth/consent requirements:
- PHI/external-egress boundary:

## Implementation order
1. Contract, if needed
2. Port
3. Mock/offline adapter
4. Domain/service behavior
5. API route
6. Generated OpenAPI/client
7. Frontend feature

## Acceptance criteria
- [ ]
- [ ]

## Verification
- Focused command:
- Downstream commands:
- Manual/browser check:

## Rollback
<How to disable or revert safely?>

## Documentation to update
- `docs/STATUS.md`:
- `docs/INTEGRATIONS.md`:
- ADR or model card:
```

## Standard delivery loop

```text
Understand → Specify → Implement → Verify → Review → Document → Commit
```

### 1. Understand

- Confirm the active runtime path.
- Find existing contracts, ports, services, routes, and generated artifacts.
- Search for callers before changing an interface.
- Identify whether the requested capability is live, mocked, or planned.

### 2. Specify

- Write acceptance criteria before implementation.
- Add an ADR before widening a contract, adding a dependency/provider/model,
  changing a security boundary, or reactivating a legacy tree.
- Define offline/demo behavior separately from external-provider behavior.

### 3. Implement

Prefer this dependency direction:

```text
contract → port → mock adapter → service/domain → API → generated client → UI
```

Keep changes bounded to the task packet. Do not mix a feature with a broad
refactor unless the refactor is the task and its callers are tested.

### 4. Verify

- Run the focused check first.
- Run every downstream command in `docs/REGRESSION.md`.
- Run the full relevant gate before declaring completion.
- Capture exact commands and results; never report a check that was not run.

### 5. Review

The reviewer must be independent from the implementation pass when possible and
must look for:

- domain purity/import violations;
- PHI logging or external-egress leaks;
- missing auth, consent, timeout, retry, or idempotency behavior;
- contract/client drift;
- mock behavior presented as live behavior;
- critical-patient commercial-flow bypass failures;
- accessibility and offline regressions;
- tests that assert implementation details instead of user behavior.

### 6. Document

Update only the canonical owner of changed facts:

- structure → `docs/ARCHITECTURE.md`;
- current health/limitations → `docs/STATUS.md`;
- provider/mock state → `docs/INTEGRATIONS.md`;
- commands/test evidence → `docs/TESTS.md`;
- durable decision → `docs/decisions/`;
- product vocabulary/scope → `docs/CONTEXT.md`.

### 7. Commit

Use one logical commit per capability:

```text
feat(scope): add capability
fix(scope): correct behavior
test(scope): add regression coverage
refactor(scope): preserve behavior while restructuring
docs(scope): update canonical guidance
chore(scope): maintain tooling
```

## Agent roles

Roles are boundaries, not separate codebases:

| Role | Primary responsibility | Must return |
|---|---|---|
| Architect | contracts, ports, package boundaries, ADRs | dependency/impact map and acceptance criteria |
| Backend | domain, services, adapters, routes | code, tests, API impact, evidence |
| Frontend | shadcn/theme, views, generated client, accessibility | UI change, states, responsive/a11y evidence |
| ML | model registry, calibration, evaluation, model cards | metrics, thresholds, limitations, reproducibility |
| Blender/3D | `.blend` scenes, GLB export, manifests, fallbacks | asset manifest, export command, performance fallback |
| Integrations | provider adapters and operations | auth, timeout, retry, webhook, sandbox evidence |
| Security | PHI, secrets, auth, trust boundaries | risk findings and required gates |
| QA | regression, contract, E2E, accessibility, offline tests | command output and gap list |
| Release | version, build, deployment, rollback | release evidence and unresolved risks |

## Handoff format

End every non-trivial session with:

```markdown
## Handoff — <date>

### Goal

### Completed
-

### Files changed
-

### Evidence
- Command: `<exact command>`
  Result: `<exit code / summary>`

### Not completed
-

### Risks or blockers
-

### Next concrete step

### Do not recreate
<Intentional removals, rejected approaches, or mock/live boundaries.>
```

## Model and integration claims

Agents must use these labels precisely:

- `mock` means local simulated behavior.
- `real` may mean local model assets or a provider-capable adapter; it does not
  automatically mean clinically validated or externally connected.
- `sandbox` means a provider test environment with dated evidence.
- `verified live` requires external delivery/readback proof and an owner.

Never promote a feature based on a UI card, seed record, fixture, or passing mock
test alone.
