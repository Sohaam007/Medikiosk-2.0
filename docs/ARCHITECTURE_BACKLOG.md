# MediKiosk 2.0 — Future Capability Map

The detailed pre-refresh architecture backlog is archived at
`docs/archive/ARCHITECTURE_BACKLOG-legacy-2026-10-22.md`. It is not an active
task queue and must not be implemented item-by-item.

This one-page map keeps the useful future direction visible without making a
large speculative feature list look like committed scope. The active sequence
is `docs/ROADMAP.md`; current truth is `docs/STATUS.md`.

## Product-scale capability groups

### 1. Community screening and preventive care

- Batch/community screening campaigns.
- Offline capture and store-and-forward sync.
- De-identified aggregate dashboards.
- Risk-to-referral follow-up queue.
- Cognitive, metabolic, respiratory, and multi-disease model slots.

### 2. Clinical intake and safety

- Multilingual voice/touch/document intake.
- Proxy/caregiver workflow.
- Clinical question protocols and human fallback.
- Vitals/NEWS2 and deterministic veto rules.
- Medication interaction and pharmacist review.
- Clinician-approved care plans and follow-up.

### 3. Interoperability and health records

- Validated FHIR R4 export.
- Destination-specific EHR/HIS adapters.
- ABDM/ABHA sandbox and later production promotion.
- Consent-based digital health passport.
- Expiring shares, revocation, purge, and audit.

### 4. Care navigation and medical tourism

- Facility and specialist catalog with freshness timestamps.
- Transparent routing by condition, language, budget, location, insurance, and
  verified availability.
- Care navigator workspace.
- Referral outcome tracking.
- Travel-readiness information without automatic booking or visa promises.

### 5. Patient experience and explainability

- Custom shadcn-compatible design system.
- Landing page and partner-facing product story.
- Optional Blender/GLB/Three.js heart and patient-education assets.
- Static/2D and low-power fallbacks.
- Multilingual education library.
- Accessibility and kiosk hardware support.

### 6. Provider and operations platform

- WhatsApp/SMS/email delivery with consent and receipts.
- Payments/UPI with webhook verification and reconciliation.
- PostgreSQL migrations and Redis adapter.
- Provider health/readiness, metrics, traces, and incident runbooks.
- Kiosk fleet telemetry and edge hardening.

## Promotion rule

Every capability moves through:

```text
idea → bounded task → contract/port → mock → tests → sandbox → verified live
```

No capability in this map is promised to users until it appears in the current
status and integration matrix with executable evidence.
