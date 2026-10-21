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

Before implementation, find the feature in `docs/FEATURES.md` and read or create
its bounded packet under `docs/tasks/active/`. The packet is the agent's scope
contract; an unbounded request must be narrowed before code is changed.

## Human accountability model

AI agents operate under five named human owners; they do not replace ownership:

| Human owner | Agent lanes | Final accountability |
|---|---|---|
| **Soham — leader** | architect/backend/clinical-safety | contracts, architecture, safety, final claims |
| **Soumyadeep — co-lead** | product/frontend/accessibility/demo | user experience, API/UI alignment, demo narrative |
| **Swapnil** | ML/model/3D | evaluation, calibration, explainability, model claims |
| **Pabitra** | QA/security/release | reproducibility, regression, CI, evidence, release gates |
| **Aditya** | integrations/data/workflow | mocks, fixtures, provider seams, integration truth |

Use `docs/TEAM_CAPACITY.md` for the current workstream matrix and
`docs/team/` for the detailed role charter. One human owner must be named in
every task packet even when several AI agents contribute.

## Two operating modes

### SEVA demo mode

Optimize for one reliable, repeatable local path:

```text
CardioVision → intake → clinician handoff → evidence package
```

Do not add live providers, broad model families, booking, payment, travel, or
large architectural migrations during the demo freeze unless Soham explicitly
opens a scope exception and Pabitra adds a regression gate.

### Product scale mode

After the demo freeze, work may proceed in parallel across frontend, model,
integration, and operations lanes. New capabilities still require a mock-first
contract, an owner, a reviewer, and a promotion gate.

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

Push the commit only to the task branch and open or update a pull request. Never
push directly to `main` or `master`, and never merge the PR. The human owner
merges only after the required reviewer approvals and protected CI checks pass.
The PR must link the feature ID, task packet, exact commands, generated-artifact
changes, and remaining risks.

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

## Named workstream routing

| Request type | Route first to | Required second review |
|---|---|---|
| Contract, API, clinical rule, ADR | Soham | Affected owner + Pabitra |
| UI, design system, landing, kiosk | Soumyadeep | Soham for clinical/API changes |
| CardioVision, model, evaluation, explainability | Swapnil | Soham + Pabitra |
| Provider adapter, mock, fixture, webhook | Aditya | Soham + Pabitra |
| Test, CI, security evidence, release/demo | Pabitra | Affected owner + Soham |

Do not dispatch the same file to two writers. If a task crosses lanes, split it
at the contract or artifact boundary and make the dependency explicit.

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
