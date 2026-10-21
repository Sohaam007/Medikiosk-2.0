# MediKiosk 2.0 — Professional Delivery Roadmap

This roadmap turns the product vision into bounded, verifiable phases. Each
phase has a goal, files, dependencies, and a gate. Do not mark a phase complete
from UI appearance alone; use the evidence described in the gate.

## Product north star

```text
Screen → Intake → Explain → Route → Travel → Heal → Follow-up
```

## Phase 0 — Repository and documentation foundation

**Goal:** make the project safe for humans and agents to extend.

**Files/surfaces:** `AGENTS.md`, `README.md`, `docs/CONTEXT.md`,
`docs/ARCHITECTURE.md`, `docs/STATUS.md`, `docs/INTEGRATIONS.md`,
`docs/TESTS.md`, `docs/REGRESSION.md`, `.governance/docs-map.json`, CI files.

**Work:** push the clean baseline, establish `main`, repair CI syntax, add
CODEOWNERS/PR templates, classify legacy trees, and remove stale production
claims from current docs.

**Gate:** clean clone setup, local test/build checks, docs-link audit, no secrets
or local patient data tracked, and CI workflow parsed successfully.

## Phase 1 — Architecture bootstrap and modularization

**Goal:** create stable seams for future capabilities without breaking the
working prototype.

**Files:** `src/medikiosk/domain/`, `ports/`, `services/`,
`api/dependencies/container.py`, future `application/` and `bootstrap/`, ADRs,
contract/invariant tests.

**Work:** introduce use-case command/query boundaries where useful, reduce large
route/view responsibilities, preserve existing contracts, and make every new
external capability port-first.

**Gate:** import/purity invariants, full backend suite, generated OpenAPI/client
sync, frontend build, and no behavior regression in the live stack test.

## Phase 2 — Design system and landing experience

**Goal:** replace scattered styling with a custom shadcn-compatible MediKiosk
theme and a credible product landing page.

**Files:** `frontend/components.json`, `frontend/src/components/ui/`,
`frontend/src/styles/tokens.css`, `theme.css`, `globals.css`, layout shell,
landing page, accessibility/visual tests.

**Work:** build tokenized medical navy/clinical blue/cardio red/emerald/saffron
theme, reusable components, responsive states, kiosk touch sizing, dark clinician
mode, reduced motion, and the Screen → Follow-up narrative.

**Gate:** no arbitrary repeated color tokens in new UI, lint/build pass, keyboard
and screen-reader review, touch-target audit, and documented screenshots.

## Phase 3 — CardioVision platform and model governance

**Goal:** make cardiovascular screening a reproducible, calibrated, explainable
model capability rather than a single adapter.

**Files:** `domain/screening/`, model contracts, model registry port/adapter,
`models/cardiovision/model-card.md`, manifest, `eval/`, screening tests,
CardioVision UI.

**Work:** add model version metadata, feature schema, missing-data policy,
calibration metadata, threshold policy, subgroup metrics, uncertainty display,
clinician-review gates, and explicit non-diagnostic language.

**Gate:** reproducible evaluation report with ROC-AUC/PR-AUC/calibration/subgroup
metrics, deterministic regression set, model card, and safe UI/API behavior.

## Phase 4 — Blender and 3D explainability pipeline

**Goal:** provide an optional, performant 3D explanation layer for CardioVision
and future patient education.

**Files:** `blender/`, `.blend` scenes, export scripts, GLB manifests,
`frontend/src/components/three/`, capability/fallback components,
`docs/BLENDER_PIPELINE.md`.

**Work:** create synthetic heart and patient assets, export reproducibly to GLB,
lazy-load in the frontend, map explainability factors to visual overlays, and
provide static/2D fallback for low-power devices and reduced motion.

**Gate:** clean-machine export, asset manifest validation, bundle-size/performance
budget, no patient likeness, keyboard/text fallback, and frontend smoke test.

## Phase 5 — Multi-disease screening registry

**Goal:** add cognitive, metabolic, respiratory, and multi-disease screening
without duplicating CardioVision-specific plumbing.

**Files:** `domain/screening/registry.py`, model contracts, per-domain modules,
evaluation reports, model cards, registry adapter, API/UI selectors.

**Work:** standardize `ScreeningModelPort`, model lifecycle, versioning,
calibration, missing-input handling, veto thresholds, and clinician review.

**Gate:** each model has contract/unit/evaluation coverage and the orchestrator
can run with one model, several models, or no model offline.

## Phase 6 — Specialist, hospital, and medical-tourism routing

**Goal:** route patients to appropriate reviewed options using condition, budget,
location, language, insurance, travel, and verified availability constraints.

**Files:** routing/tourism/travel domain contracts, ports, local fixtures,
provider adapters, API schemas/routes, matching UI, audit tests.

**Work:** implement transparent weighted ranking and constraint explanations.
Critical patients bypass commercial routing. No booking, payment, visa, or
capacity guarantee occurs without an explicit provider and confirmation flow.

**Gate:** deterministic ranking fixtures, safety-veto tests, provider freshness
rules, explainable recommendation output, and no automatic consequential action.

## Phase 7 — Integration promotion ladder

**Goal:** replace mocks with governed sandbox and production adapters one at a
time.

**Order:** ABDM/ABHA → FHIR/EHR → PM-JAY/insurance → WhatsApp/SMS → payments →
pharmacy/interactions → travel/partner systems.

**Files:** `ports/`, `adapters/`, integration tests, provider runbooks,
`docs/INTEGRATIONS.md`, secret/config management, health checks.

**Gate:** mock contract tests, sandbox evidence, auth/signature verification,
timeouts/retries/idempotency, PHI egress review, delivery/readback proof, and
rollback procedure.

## Phase 8 — Digital health passport and follow-up

**Goal:** make the interaction longitudinal and consent-controlled.

**Files:** passport/followup domain modules, contracts, ports, local adapter,
expiry/revocation logic, patient pages, consent/share UI, scheduled delivery.

**Gate:** consent, expiry, revoke, audit, export, delivery failure, and purge
tests; no permanent unauthenticated PHI URLs.

## Phase 9 — Production operations and physical deployment

**Goal:** make the platform operable, observable, secure, and deployable.

**Files:** `.github/workflows/`, Docker/Compose, migrations, observability,
runbooks, deployment scripts, edge kiosk scripts, security tests.

**Work:** managed secrets, PostgreSQL migrations, Redis adapter, metrics/traces,
rate limiting, backup/restore, disaster recovery, kiosk hardening, fleet
telemetry, provider monitoring, vulnerability scanning, and incident drills.

**Gate:** clean Linux build, container smoke, restore test, security scan,
provider failure drill, rollback drill, and clinical governance sign-off.

## Work selection rule

Choose the smallest incomplete phase deliverable that unlocks the next user
outcome. Every task must reference one phase, one bounded owner, one acceptance
set, and one regression map row. Do not start a provider integration before its
mock contract and failure policy exist.
