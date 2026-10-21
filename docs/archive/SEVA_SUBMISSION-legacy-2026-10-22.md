# SEVA 2026 submission package — MediKiosk 2.0

## One-line pitch

MediKiosk 2.0 turns a community health kiosk into a safe care corridor:
CardioVision screens cardiovascular risk, MediKiosk captures multilingual
history and documents, FHIR preserves a portable record, and the clinician
queue makes the next step visible.

## Demonstrable scope

| Journey | Working evidence |
|---|---|
| Screen | `POST /api/screening/cardiovascular`, local CardioVision assets and the visible `CardioVisionPanel` |
| Intake | Existing voice/touch and SOCRATES conversation flow in `KioskIntakeView` |
| Connect | `POST /api/screening/cardiovascular/referral` produces deterministic cardiology candidate IDs from available local doctor/package fixtures; clinician review remains required |
| Heal | FHIR/ABDM-oriented contracts, summaries, audit events and document workflow |
| Follow-up | Existing offline queue, caregiver pass and mock WhatsApp adapter |

## Five-minute demo script

1. Start the backend and frontend using the commands in the root README.
2. Open the patient kiosk and choose Hindi or English.
3. In Stage 3, enter an age, select hypertension and typical chest pain, then
   press **Run heart screen**.
4. Point out the probability, whole-vessel comparison and screening disclaimer.
5. With a configured kiosk JWT, point out the cardiology candidate count and
   the explicit “no doctor selected / no package purchased” safety boundary.
6. Stop the backend or leave auth unconfigured and repeat the action to show the
   explicitly labelled offline preview.
7. Continue through voice/touch intake and open the clinician console to show
   the handoff surface.
8. For an API-only proof, post the screening and referral sample payloads from
   the root README and
   show the structured JSON response.

## Claims we do and do not make

We claim a working local software prototype, deterministic offline fallback,
structured contracts and a bounded integration of the supplied CardioVision
assets. We do not claim clinical validation, diagnostic accuracy, live ABDM,
WhatsApp, ambulance, payment, hospital-capacity or visa integrations. Those
are explicitly staged behind adapters or fixtures in the plan.

## Architecture

```text
Vite kiosk / clinician console
              |
        FastAPI routes
              |
   CardiovascularScreeningPort ---- existing intake/services
              |                              |
 CardioVision adapter                   FHIR + audit + offline queue
       |           |
 mock/offline   local XGBoost assets
```

## Submission checklist

- [x] Reproducible Python and Node runtime pins
- [x] Python and frontend lockfiles
- [x] `.env.example` without secrets
- [x] Dockerfile with pinned `uv` image and correct ASGI factory
- [x] Single backend test command: `make test`
- [x] API, unit, invariant and frontend build checks documented
- [x] Deterministic referral candidate policy with clinician-review disclaimer
- [x] Product vision and registration material retained in this folder
- [ ] Insert fresh screenshots and demo URL into the PowerPoint template
- [ ] Human clinical/usability review before any real patient deployment
- [ ] External SEVA/OmniRush website upload by the project owner
