# MediKiosk 2.0 Documentation Spine

Use this page to navigate the project without loading every document.

## New coding session

```text
AGENTS.md
→ docs/CONTEXT.md
→ docs/ARCHITECTURE.md
→ docs/STATUS.md
→ docs/INTEGRATIONS.md
→ docs/TESTS.md
→ docs/FEATURES.md
→ docs/tasks/active/README.md
→ task-specific files and ADRs
```

## Canonical roles

| Role | Canonical source |
|---|---|
| Agent constitution | `AGENTS.md` |
| Product context/vocabulary | `docs/CONTEXT.md` |
| Current architecture/map | `docs/ARCHITECTURE.md` |
| Current health and blockers | `docs/STATUS.md` |
| Team capacity and ownership | `docs/TEAM_CAPACITY.md` and `docs/team/` |
| SEVA demo scope | `docs/SEVA_SUBMISSION.md` |
| Live/mock integration truth | `docs/INTEGRATIONS.md` |
| Test and verification commands | `docs/TESTS.md` |
| Downstream regression map | `docs/REGRESSION.md` |
| Product requirements | `docs/PRODUCT_REQUIREMENTS.md` |
| Sequenced roadmap | `docs/ROADMAP.md` |
| Active feature register | `docs/FEATURES.md` |
| Active task packets | `docs/tasks/active/` |
| Agent operating model | `docs/AI_ORCHESTRATION.md` |
| Engineering rules | `docs/ENGINEERING.md` |
| Security/privacy | `docs/SECURITY.md` |
| Frontend rules | `frontend/README.md` |
| Durable decisions | `docs/decisions/README.md` and `docs/decisions/` |

## Supporting guides

- `docs/MODEL_GOVERNANCE.md` — model lifecycle and evidence.
- `docs/BLENDER_PIPELINE.md` — future 3D asset workflow.
- `docs/DESIGN_SYSTEM.md` — custom shadcn-compatible visual system.
- `docs/OPERATIONS.md` — deployment, observability, and incident expectations.
- `docs/reviews/PLAN_REVIEW_RESPONSE-2026-10-22.md` — adopted response to the external plan review.
- `docs/DEMO_EVIDENCE.md` — screenshots, recordings, and claim review.
- `submission/` — final judge-facing materials; raw and draft subdirectories are ignored.
- `docs/CLINICAL_REGULATORY.md` — intended-use, pilot, and regulatory readiness.
- [`docs/team/README.md`](team/README.md) — named human owners and AI-agent lanes.
- `docs/FRONTEND_HANDOFF.md` — current frontend/API handoff.
- `docs/UNVERIFIED.md` — current environment-dependent verification gaps.
- `docs/ARCHITECTURE_BACKLOG.md` — concise future capability map; old drafts are local-only.
- `docs/archive/README.md` — boundary for historical material kept outside the tracked tree.
- `docs/templates/` — feature, integration, model, and handoff packets.
- `scripts/check_repo_hygiene.py` — dependency-free tracked-file and active-doc check.
- `docs/CONTRACTS.md` — domain contract reference.
- `docs/openapi.json` — generated HTTP contract.

## Evidence rule

When docs conflict with code/configuration/tests, record the discrepancy and use
the executable source as truth until the canonical document is corrected.
