# SEVA 2026 Submission Package — MediKiosk 2.0

**Scope freeze:** Demo Track A only. Product Scale Track B is future work and
must not be presented as implemented in the SEVA submission.

## One-line pitch

MediKiosk 2.0 turns a community health kiosk into a safe care corridor:
CardioVision screens cardiovascular risk, MediKiosk captures multilingual
history and documents, a clinician reviews the structured handoff, and the next
care option remains visible without pretending that a mock is a live provider.

## Team

| Person | Submission responsibility |
|---|---|
| Soham | Scope freeze, architecture, clinical safety, final claims |
| Soumyadeep | Kiosk/clinician experience, landing/demo narrative |
| Swapnil | CardioVision model card and evaluation methodology |
| Pabitra | Verification, screenshots, recording, release evidence |
| Aditya | Synthetic fixtures, reset path, integration truth, edge cases |

## Demonstrable scope

| Journey | Local evidence | Claim label |
|---|---|---|
| Screen | `/api/screening/cardiovascular`, CardioVision panel, local mock/assets | Mock/simulated by default; optional local model assets; not clinical validation |
| Explain | Risk factors, model/version metadata, disclaimer, local explanation | Local explanation aid; not diagnosis |
| Connect | `/api/screening/cardiovascular/referral`, local cardiology candidates | Local non-binding candidates; no booking, payment, or live capacity |
| Intake | Voice/touch/SOCRATES path in `KioskIntakeView` | Local workflow; speech transcription is mock/simulated |
| Documents | Synthetic document capture and OCR boundary | Provider-capable but unverified; no real PHI |
| Clinician handoff | Queue, summary, audit, FHIR-shaped local output | Local structured handoff; not externally FHIR-validated |
| Resilience | Offline preview, auth failure, reset/demo case | Local fallback; not provider delivery |

## Five-minute demo script

1. Run `start_dev.bat` or the documented manual commands.
2. Open the kiosk and choose Hindi or English.
3. Select patient or informant and use the deterministic synthetic case.
4. Run the CardioVision heart screen.
5. Show risk output, top factors, model/version metadata, missing-data behavior,
   and the visible screening-only disclaimer.
6. Show cardiology candidate count and the explicit no-doctor-selected,
   no-package-purchased safety boundary.
7. Continue through voice/touch/document intake.
8. Open the clinician console and show the queue, review story, and local
   summary/FHIR-shaped handoff.
9. Stop the backend or remove auth and show the clearly labeled offline/failure
   behavior.
10. Reset and repeat the synthetic case to prove repeatability.

## Claims we do and do not make

We claim a working local software prototype, deterministic offline behavior,
structured contracts, a bounded CardioVision screening path, and a
clinician-review handoff. The exact claim labels for the demonstrable journey
are defined in the table above and must remain aligned with
`docs/INTEGRATIONS.md`.

We do not claim clinical validation, `>90% AUC`, diagnosis, live ABDM, PM-JAY,
WhatsApp, ambulance, payment, hospital capacity, visa, travel, or live
medical-tourism integrations. Local fixtures, UI cards, mock gateways, and
provider-capable adapters without dated sandbox evidence do not count as live
connectivity.

## Submission evidence

Track artifacts using `docs/DEMO_EVIDENCE.md`. Required before submission:

- [x] Runtime pins and lockfiles.
- [x] Dockerfile and one-click launcher.
- [x] Backend tests, invariants, lint, mypy, and frontend build documented.
- [x] Deterministic referral policy and safety disclaimer.
- [ ] Dated screenshots.
- [ ] Screen recording.
- [ ] Clean-clone verification log.
- [ ] Human clinical/usability review plan.
- [ ] External SEVA/OmniRush upload by the project owner.

## Future product boundary

ABDM/ABHA, PM-JAY, communications, payments, hospital/EHR, medical tourism,
multi-disease screening, digital passport, follow-up, Blender/3D, and production
operations belong to Track B in `docs/ROADMAP.md`.
