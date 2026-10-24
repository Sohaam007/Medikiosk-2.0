# Aditya — Integrations, Synthetic Data and Workflow Reliability

## Mission

Make local/demo workflows deterministic now and make future provider integrations
safe to promote later.

## Owns

- Synthetic patient, document, screening, and referral fixtures.
- Mock adapters and integration boundary tests.
- `docs/INTEGRATIONS.md` and `docs/UNVERIFIED.md` updates.
- Demo reset/seed behavior and edge-case workflow fixtures.
- Community screening/campaign mode discovery.
- Future provider catalog, hospital routing, and partner-data seams.

## Must review

- Any change that claims external delivery or live capacity.
- Fixture changes that affect model/UI behavior.
- Webhooks, SSE, notifications, document inputs, and provider errors.
- Consent and PHI behavior at integration boundaries.

## SEVA deliverables

- One deterministic synthetic demo case.
- Resettable local data path.
- Mock/timeout/error fixtures for CardioVision, OCR, referral, PM-JAY, and
  communications.
- Accurate integration matrix and unverified-items log.

## Competition launch

- Primary packet: [F-003 — Demo Reset and Failure Fixtures](../tasks/active/F-003-demo-reset-fixtures.md).
- Evidence handoff: give the reset command, fixture manifest, failure matrix,
  and integration-truth changes to Pabitra and Soham.
- Review gate: keep all fixtures synthetic and do not promote a provider,
  webhook, notification, or capacity claim without a separate boundary review.

## Stop conditions

Stop when a fixture uses real patient data, a provider adapter lacks a mock/error
path, a webhook lacks replay/auth handling, or a local catalog is described as
live capacity.
