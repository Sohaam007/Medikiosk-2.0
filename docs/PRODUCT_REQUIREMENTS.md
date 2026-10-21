# MediKiosk 2.0 — Product Requirements

## Outcome

Build a safe, multilingual, extensible health-journey platform that helps a
patient move from community screening to clinician-ready intake, specialist
routing, treatment/travel coordination, and consent-based follow-up.

## Primary users

- Patient using a kiosk or browser.
- Relative/caregiver/ASHA worker answering on a patient's behalf.
- Community health worker operating a kiosk.
- Clinician reviewing a queue and clinical story.
- Hospital coordinator routing care.
- Medical-tourism coordinator organizing verified options.
- Platform administrator operating integrations and fleet health.

## Required journey

```text
Screen → Intake → Explain → Route → Travel → Heal → Follow-up
```

Each step must work independently and degrade safely when the next dependency is
unavailable.

## Capability requirements

### Delivery tracks

- The SEVA Demo Track remains a reliable local vertical slice using synthetic
  data and mock/local adapters.
- The Product Scale Track may add providers, models, passports, follow-up,
  community campaigns, routing, and operations only through the promotion gates
  in `docs/ROADMAP.md` and `docs/INTEGRATIONS.md`.

### Screening

- Cardiovascular, cognitive, metabolic, respiratory, and multi-disease model
  slots behind one registry contract.
- Model/version/calibration metadata visible to the review surface.
- Explainable factors and missing-input warnings.
- No diagnosis language or autonomous treatment decision.
- Critical veto path independent from commercial matching.

### Community screening

- Support batch/campaign mode for community health workers and PHC-style
  outreach without requiring continuous connectivity.
- Store-and-forward records must be consented, resumable, deduplicated, and
  purgeable.
- Aggregate dashboards must use de-identified operational data and must not
  expose individual patient records.

### Intake

- Voice, touch, and document capture.
- 8+ Indian languages with language-specific copy and audio behavior.
- Patient/proxy informant identification.
- Clinical question protocol and frustration/human-fallback behavior.
- Consent, audit, purge, and source/confidence metadata.

### Interoperability

- Local structured domain contracts.
- FHIR R4 export with real validator before any compliance claim.
- ABDM/ABHA adapter with consent and signed callback boundary.
- Hospital/EHR destination adapters behind ports.

### Routing and medical tourism

- Transparent ranking by condition, specialty, language, location, budget,
  insurance, travel constraints, verified availability, and follow-up ability.
- Recommendation explanation and freshness timestamps.
- Human confirmation before booking, payment, or travel action.

### Care navigation and continuity

- Track referral status without claiming treatment outcome.
- Provide a care navigator workspace for missing documents, language needs,
  budget constraints, and next human action.
- Provide consented caregiver access with expiry, revoke, and audit behavior.
- Provide clinician-approved education and follow-up content with delivery,
  retry, opt-out, and escalation state.

### Engagement and follow-up

- WhatsApp/SMS/email provider adapters with opt-in, templates, delivery status,
  retry, opt-out, and escalation.
- Digital health passport with expiring shares and revocation.
- Care plans and reminders with clinician-approved content.

### Experience and 3D

- Custom shadcn-compatible design system, not scattered default utility styling.
- Landing page explaining the complete journey and safety model.
- CardioVision 3D explanation using Blender-exported assets.
- Static/2D fallback, reduced motion, low-power behavior, and accessible text.

## Non-functional requirements

- Reproducible setup on a clean Linux machine and local Windows development.
- Offline demo mode with deterministic mocks.
- No PHI in logs, source, fixtures, telemetry, or documentation.
- Strict type checking, linting, generated API client, and contract tests.
- Bounded requests, uploads, queues, provider timeouts, retries, and idempotency.
- Auditability for consent, external sharing, clinical overrides, and purge.
- Model evaluation with AUC, calibration, subgroup, and safety-threshold evidence.
- Accessibility suitable for large-touch kiosk interaction.
- Clinical/regulatory readiness evidence before real-patient pilot use.

## Explicit non-goals without separate approval

- Autonomous diagnosis or treatment.
- Automatic surgery/doctor/package booking.
- Unverified live capacity or medical-tourism guarantees.
- Emergency dispatch without an approved operational provider.
- Sending PHI to a provider without consent, contract, and security review.
- Claiming `>90% AUC`, FHIR compliance, ABDM connectivity, or production readiness
  without dated evidence.

## Definition of done

A capability is done only when:

1. its contract and ownership are clear;
2. its offline/mock behavior is deterministic;
3. its API/client/UI path is complete if user-facing;
4. focused and downstream tests pass;
5. security/privacy and clinical safety boundaries are reviewed;
6. generated artifacts are synchronized;
7. canonical documentation and status are updated;
8. rollback and unverified gaps are recorded.
