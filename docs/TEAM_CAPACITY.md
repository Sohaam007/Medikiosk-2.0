# MediKiosk 2.0 — Five-Person Capacity and Workstreams

**Effective team model:** October 22, 2026

This document converts the product roadmap into work that five people can run
in parallel without creating five competing implementations. Soham is the team
leader; Soumyadeep is the co-lead. The other three owners have bounded lanes and
must use the shared contracts, regression map, and evidence gates.

## Team roster

| Person | Role | Accountable lane | Primary outputs |
|---|---|---|---|
| **Soham** | **Leader — Architecture, Backend, Clinical Safety** | Product scope, contracts, backend, ADRs, clinical/privacy boundaries, final claims | `src/medikiosk/domain`, `ports`, `services`, API architecture, ADRs, final merge decisions |
| **Soumyadeep** | **Co-lead — Product Experience, Frontend, Demo Narrative** | Kiosk, clinician console, design system, accessibility, demo/pitch experience | `frontend/`, generated client consumption, screenshots, judge-facing flow |
| **Swapnil** | **ML/AI and CardioVision Lead** | Model governance, evaluation, explainability, future Blender/3D | `models/`, `eval/`, CardioVision contracts/fixtures, model cards, 3D asset plan |
| **Pabitra** | **QA, Security Verification, Release Operations** | Test strategy, CI, clean-clone verification, security gates, release evidence | `tests/`, `.github/`, verification reports, demo recording, deployment/runbooks |
| **Aditya** | **Integrations, Synthetic Data, Workflow Reliability** | Mock/provider seams, synthetic fixtures, document/referral edge cases, community workflows | `adapters/` integration support, fixtures, integration matrix, reset/demo data, future partner seams |

## Leadership rules

- **Soham is the final decision owner** for architecture, contracts, clinical
  safety, privacy, and production claims.
- **Soumyadeep is the final decision owner** for product interaction, frontend
  composition, accessibility, and demo narrative, within the agreed contracts.
- Soham and Soumyadeep jointly approve scope changes that affect both API and UI.
- Swapnil cannot publish model-performance claims without Soham's safety review
  and Pabitra's reproducibility evidence.
- Aditya cannot promote an integration from mock to sandbox without Soham's
  boundary review and Pabitra's contract/failure tests.
- Pabitra can block a release for missing evidence, broken reproducibility,
  security findings, or an unverified claim.

## SEVA Demo Track ownership

The near-term demo is intentionally narrower than the full product roadmap:

```text
Language/informant
→ CardioVision screen
→ explanation and clinician-review boundary
→ local non-binding referral candidates
→ multilingual intake/document path
→ clinician queue and local summary/FHIR-shaped handoff
```

| Deliverable | Accountable | Reviewer | Parallel dependency |
|---|---|---|---|
| Scope/claim freeze and final acceptance | Soham | Soumyadeep | Blocks new contracts and public claims |
| Kiosk/clinician UI polish | Soumyadeep | Soham + Pabitra | Uses current generated client |
| CardioVision evidence pack | Swapnil | Soham + Pabitra | Uses current local model/assets |
| Synthetic fixtures and deterministic reset | Aditya | Pabitra | Must not contain PHI |
| Full verification, screenshots, recording, clean-clone proof | Pabitra | Soham + Soumyadeep | Runs after feature branches stabilize |

## Product Scale Track ownership

After the demo freeze, the team can expand in parallel:

| Product lane | Owner | First useful expansion |
|---|---|---|
| Clinical platform | Soham | Screening registry, care-plan domain, clinical/regulatory readiness |
| Patient and clinician experience | Soumyadeep | Custom design system, landing page, passport, accessibility, community mode UI |
| Intelligence and explainability | Swapnil | Calibrated CardioVision, cognitive/metabolic/respiratory model slots, Blender/3D |
| Provider and health-network integrations | Aditya | ABDM/FHIR/PM-JAY/communications sandbox adapters, facility catalog, routing data |
| Quality and operations | Pabitra | CI security gates, observability, migrations, offline sync verification, release automation |

## Parallel execution rules

The lanes may work concurrently only when their write surfaces are isolated:

```text
Soham: contracts/domain/API boundaries
Soumyadeep: frontend/features/components/styles
Swapnil: models/eval/ML fixtures/blender planning
Aditya: adapters/integration fixtures/docs integration matrix
Pabitra: tests/.github/release evidence/runbooks
```

If two lanes need the same contract, Soham creates or approves the contract
first. If two lanes need the same frontend view, Soumyadeep creates the seam or
the work becomes sequential. Do not solve collisions by duplicating types or
parallel implementations.

## Capacity limits

- One person may own at most two active task packets at once.
- Each task packet must fit a reviewable 1–3 day slice or be split again.
- No more than two provider integrations may be in sandbox work simultaneously.
- No more than one model may be promoted to evaluation review at a time.
- Demo evidence starts only after the final UI/API contract freeze.
- Product-scale work cannot weaken the frozen SEVA demo path.

## Escalation and substitutes

The team does not currently include a clinical advisor, regulatory counsel, or
hospital partner. Before pilot or live patient use, add those external reviewers
as explicit approval gates. Team members may prepare evidence and questions, but
must not self-certify clinical validation, regulatory classification, or live
provider compliance.
