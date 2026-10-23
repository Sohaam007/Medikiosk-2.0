# MediKiosk 2.0 — Two-Track Delivery Roadmap

This roadmap separates what the five-person team can make reliable for the SEVA
2026 submission from the larger product that can be built after the demo freeze.
The team may expand the product roadmap, but it must not destabilize the frozen
demo path.

## North-star journey

```text
Screen → Intake → Explain → Route → Travel → Heal → Follow-up
```

## Track A — SEVA Demo Release

**Goal:** deliver a reliable, evidence-backed local vertical slice rather than a
wide set of unverified integrations.

### Frozen demo journey

```text
Language/informant selection
→ CardioVision screen
→ explanation + screening disclaimer
→ non-binding local cardiology candidates
→ multilingual voice/touch/document intake
→ clinician queue/review
→ local summary/FHIR-shaped handoff
→ reset/offline/auth-failure demonstration
```

### Demo workstreams

| Workstream | Owner | Gate |
|---|---|---|
| Scope, contracts, safety, final claims | Soham | No unsupported provider/model/clinical claim remains |
| Kiosk, clinician console, landing/demo polish | Soumyadeep | Accessible, responsive, resettable, no fake success |
| CardioVision model/evidence pack | Swapnil | Manifest, model card, deterministic evaluation methodology |
| Synthetic fixtures/mock boundaries/reset | Aditya | No PHI, stable demo case, failure paths visible |
| QA, CI, screenshots, screen recording, clean clone | Pabitra | Full checks and dated evidence package pass |

### Track A acceptance gate

- `make test` passes.
- Ruff check/format and strict mypy pass.
- Frontend lint/build pass.
- Launcher/backend/frontend smoke passes.
- CardioVision mock/local mode is visibly labeled and non-diagnostic.
- Referral candidates remain non-binding; no booking/payment/capacity claim.
- Synthetic reset case works repeatedly.
- Offline/auth failure does not look like external success.
- Screen recording, screenshots, and one-page judge summary exist.
- `docs/INTEGRATIONS.md`, `docs/STATUS.md`, and `docs/DEMO_EVIDENCE.md` agree.

### Deferred from Track A

- Live ABDM/ABHA, PM-JAY, WhatsApp, payments, hospital/EHR, ambulance, travel,
  and medical-tourism providers.
- Cognitive, metabolic, respiratory, and multi-disease models.
- Full digital health passport and automated follow-up.
- Blender/GLB/Three.js as a release blocker; a static 2D explanation is allowed.
- Live hospital capacity, booking, visa, treatment, or travel guarantees.
- Physical kiosk hardware validation.
- Production Redis, migrations, observability, backup, and incident operations.

## Track B — Product Scale Roadmap

### Phase B1 — Clinical and platform readiness

**Owner:** Soham; **support:** Swapnil, Pabitra

- Screening registry and model lifecycle contracts.
- Clinical/regulatory intended-use assessment.
- Care-plan and follow-up domain boundaries.
- Migration-controlled persistence and production configuration.
- Explicit external clinical advisor and pilot-site approval gates.

**Gate:** approved intended-use statement, model lifecycle, safety policy, and
pilot-readiness checklist.

### Phase B2 — Custom product experience

**Owner:** Soumyadeep; **support:** Pabitra, Swapnil

- Custom shadcn-compatible design system.
- Landing page explaining the full journey and honest current scope.
- Feature-based frontend decomposition.
- Digital health passport UI.
- Community screening campaign UI.
- Accessibility, low-power, reduced-motion, and offline-first experience.

**Gate:** component tokens, keyboard/touch/a11y checks, visual evidence, and no
regression in the kiosk/clinician demo.

### Phase B3 — Intelligence and 3D explanation

**Owner:** Swapnil; **support:** Soumyadeep, Soham

- Calibrated CardioVision registry.
- Cognitive, diabetes/metabolic, respiratory, and multi-disease model slots.
- Blender heart/education assets with GLB export manifest.
- Model-aware explanation overlays and 2D/static fallback.
- Community screening aggregation using de-identified data.

**Gate:** reproducible evaluation, calibration/subgroup evidence, model cards,
asset validation, performance budget, and clinician safety review.

### Phase B4 — Health-network and provider integrations

**Owner:** Aditya; **support:** Soham, Pabitra

- ABDM/ABHA sandbox adapter.
- Destination-specific FHIR/EHR adapters.
- PM-JAY/insurance sandbox.
- WhatsApp/SMS/email communications with opt-in and delivery receipts.
- Hospital/facility catalog with freshness timestamps.
- Transparent hospital/specialist/medical-tourism routing.
- Medication interaction and pharmacy safety provider seam.

**Gate:** mock → sandbox → verified-live promotion with auth/signatures,
consent, timeout/retry/idempotency, audit, readback, monitoring, and rollback.

### Phase B5 — Quality, operations, and deployment

**Owner:** Pabitra; **support:** all owners

- CI security gates, secret/dependency/container scans.
- PostgreSQL migrations, Redis adapter, observability, backups, restore tests.
- Provider health/readiness and incident runbooks.
- Kiosk hardware/edge lockdown and fleet telemetry.
- Performance, accessibility, security, and disaster-recovery evidence.

**Gate:** clean Linux build, container smoke, restore/rollback drills, external
security review, and named operational owner.

## Practical feature expansion backlog

These features increase product value without requiring unsafe automation:

1. **Community Screening Campaign Mode** — batch sessions, offline sync, de-
   identified aggregate dashboards, referral follow-up queue.
2. **Care Navigator Workspace** — coordinator view of referral status, missing
   documents, language needs, budget constraints, and next human action.
3. **Referral Outcome Tracking** — record whether a candidate was reviewed,
   contacted, attended, or declined without claiming clinical outcome.
4. **Consent and Caregiver Access** — scoped, expiring caregiver access with
   revoke/audit behavior.
5. **Medication Safety Review** — structured medication list, interaction flags,
   duplicate-therapy warnings, and pharmacist/clinician review.
6. **Patient Education Library** — multilingual, clinician-approved explainers
   for risk factors, preparation, medicines, and follow-up.
7. **Operations Health Console** — kiosk connectivity, camera/mic/printer health,
   queue latency, provider status, and zero-PHI telemetry.
8. **Evidence Dashboard** — model version, test status, integration status,
   release evidence, and known limitations for internal operators.

## Work selection rule

Choose the smallest incomplete deliverable that unlocks the next user outcome.
Every task references one track, one phase, one owner, one reviewer, one
acceptance gate, and one row in `docs/REGRESSION.md`.

## Track B explanation implementation sequence

The 3D and assistant work must follow this order rather than being developed as
an unbounded chatbot or asset-generation experiment:

1. Approve the clinical intent, allowed claims, and external-egress boundary.
2. Add the screening/model registry and typed explanation contract.
3. Build deterministic mocks, red-flag behavior, and static fallbacks first.
4. Create one clinician-reviewed CardioVision Blender scene with stable semantic
   nodes and a checked GLB manifest.
5. Integrate the viewer with loading, error, offline, unsupported-device, and
   reduced-motion states.
6. Add the bounded assistant with allowlisted actions and schema validation.
7. Run model, asset, frontend, accessibility, performance, PHI, and failure-path
   checks.
8. Obtain team review and record evidence before adding another disease system.

No disease-specific 3D scene or hosted assistant is a release blocker for Track
A. The first Track B scene must remain educational/illustrative and must not
claim a patient-specific lesion or diagnosis.
