# MediKiosk 2.0 — Ownership and Five-Person Team Model

The active team has five people. Soham is the leader and Soumyadeep is the
co-lead. Detailed capacity rules live in `docs/TEAM_CAPACITY.md`; individual
profiles live in `docs/team/`.

Profiles: [Soham](team/SOHAM.md) · [Soumyadeep](team/SOUMYADEEP.md) ·
[Swapnil](team/SWAPNIL.md) · [Pabitra](team/PABITRA.md) ·
[Aditya](team/ADITYA.md)

## Human ownership

| Owner | Role | Default ownership | Final review responsibility |
|---|---|---|---|
| **Soham** | **Leader — Architecture, Backend, Clinical Safety** | Product scope, domain, ports, services, API architecture, ADRs, privacy, clinical claims | Contracts, safety boundaries, production claims, final merge decisions |
| **Soumyadeep** | **Co-lead — Product Experience and Frontend** | Kiosk, clinician console, design system, accessibility, landing/demo narrative | UI/API alignment, clinical wording, browser behavior, judge-facing flow |
| **Swapnil** | **ML/AI and CardioVision Lead** | Models, evaluation, calibration, explainability, model cards, 3D plan | Model claims, thresholds, data provenance, explainability safety |
| **Pabitra** | **QA, Security Verification and Release Operations** | Tests, CI, clean-clone verification, security evidence, screenshots, recording, release | Evidence completeness, reproducibility, security and release gates |
| **Aditya** | **Integrations, Synthetic Data and Workflow Reliability** | Mock/provider seams, fixtures, reset/demo data, document/referral edge cases, partner-data preparation | Integration truth, fixture safety, webhook/provider failure behavior |

## Path ownership

| Path | Accountable owner | Required review |
|---|---|---|
| `src/medikiosk/domain/`, `ports/`, `services/` | Soham | Affected feature owner + Pabitra for regressions |
| `src/medikiosk/api/` | Soham | Soumyadeep when HTTP/client behavior changes |
| `src/medikiosk/adapters/` | Aditya for provider seams; Soham for architecture | Pabitra security/reliability review |
| `frontend/` | Soumyadeep | Soham for contract/clinical changes; Pabitra for a11y/release |
| `models/`, `eval/` | Swapnil | Soham safety review; Pabitra reproducibility review |
| `tests/`, `.github/`, evidence | Pabitra | Affected owner and Soham |
| Synthetic fixtures and demo reset | Aditya | Pabitra and Soumyadeep |
| `docs/`, ADRs, roadmap, status | Soham | All affected owners review their sections |

## Team operating rules

- One accountable writer per task packet; one named reviewer.
- Soham and Soumyadeep jointly approve API/UI scope changes.
- A contract change is sequential: Soham approves the contract before parallel
  frontend, ML, integration, or test work consumes it.
- Mock behavior must exist before sandbox/provider work.
- Pabitra may block a release for missing evidence or unsafe claims.
- The team must add a clinical advisor, regulatory reviewer, and pilot-site owner
  before any real-patient pilot; the five-person engineering team cannot self-
  certify those decisions.

## AI agent mapping

AI agents work under the human owner; they do not replace accountability:

| Agent lane | Human owner | Safe scope |
|---|---|---|
| Architect/backend | Soham | contracts, services, routes, ADRs, invariants |
| Product/frontend | Soumyadeep | components, views, styles, generated client, a11y |
| ML/model | Swapnil | evaluation, manifests, model cards, explainability fixtures |
| Integration/data | Aditya | mock adapters, fixtures, provider boundary tests |
| QA/release/security | Pabitra | regression, CI, smoke, evidence, security verification |

## Escalation

Blocked decisions about clinical thresholds, regulatory classification, provider
contracts, consent, PHI retention, or deployment authority must be recorded in an
ADR or readiness document; agents must not guess.
