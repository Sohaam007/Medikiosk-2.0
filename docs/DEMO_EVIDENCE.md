# MediKiosk 2.0 — Demo Evidence Plan

This is the evidence checklist for the SEVA 2026 submission and future partner
demonstrations. It is owned by Pabitra with Soumyadeep for presentation and
Soham for claims/safety approval.

## Required demo artifact set

- [ ] Dated clean-clone setup log.
- [ ] Backend/frontend launcher smoke result.
- [ ] Full test/lint/type/build result.
- [ ] Synthetic demo case manifest and reset instructions.
- [ ] CardioVision model/version/limitation screenshot.
- [ ] Kiosk-to-clinician workflow screenshots.
- [ ] Offline/auth-failure fallback screenshot.
- [ ] Screen recording of the five-minute flow.
- [ ] Judge-facing one-page summary.
- [ ] Claim matrix reviewed against `docs/INTEGRATIONS.md`.
- [ ] No real patient data, tokens, secrets, or private payloads in artifacts.

## Frozen demo path

```text
Start local stack
→ choose English or Hindi
→ select patient/informant
→ run CardioVision with synthetic features
→ inspect explanation and screening disclaimer
→ inspect non-binding cardiology candidates
→ continue intake/document path
→ show clinician queue and summary/FHIR-shaped handoff
→ show reset/offline behavior
```

## Canonical Track A claim matrix

Use the following labels when preparing screenshots, recordings, summaries, or
judge-facing material. These labels mirror the integration vocabulary in
`docs/INTEGRATIONS.md`; a local UI surface must not be described as a live
provider integration.

| Demonstrated capability | Canonical label | Evidence boundary |
|---|---|---|
| CardioVision screen | Mock/simulated by default; optional local model assets | Screening review signal only; no diagnosis or clinical validation claim. |
| Explanation | Local | Model factors and disclaimer are shown; no causal medical advice claim. |
| Referral candidates | Local | Non-binding cardiology candidates; no doctor selection, booking, payment, or capacity claim. |
| Voice/touch intake | Local; speech transcription mock/simulated | Demonstrates workflow behavior, not external speech-provider delivery. |
| Document/OCR path | Provider-capable but unverified | Synthetic fixtures only; no real patient files or verified external delivery. |
| Clinician handoff | Local | Queue, audit, summary, and FHIR-shaped output; not external FHIR compliance evidence. |
| Offline/auth-failure/reset | Local fallback | Failure must be visible and must not look like successful provider delivery. |

The statuses `sandbox-verified` and `verified live` are not used anywhere in the
SEVA demo package unless a dated, reproducible external test and readback record
has been added by the responsible owner and reviewed by Soham and Pabitra.

## Evidence naming

Use repository-relative names and dates:

```text
docs/evidence/2026-10-22-cardio-screen.png
docs/evidence/2026-10-22-kiosk-to-clinician.webm
docs/evidence/2026-10-22-verification.md
```

Do not commit large binaries or sensitive captures without an explicit repository
decision. If the submission platform needs them, keep the source in an approved
private artifact store and commit only redacted references/checksums.

## Claim review

Before publication, label each claim as:

- implemented locally;
- mock/simulated;
- provider-capable but unverified;
- sandbox-verified;
- deferred.

Never call a local FHIR-shaped bundle “FHIR-compliant” without external validator
and destination evidence. Never call a UI integration card live.
