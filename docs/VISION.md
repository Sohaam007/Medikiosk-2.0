# MediKiosk 2.0 — Product Vision

MediKiosk 2.0 is a unified, consent-aware health-journey platform for Indian
healthcare. It connects preventive screening, multilingual clinical intake,
explainable routing, treatment/travel coordination, and follow-up continuity.

## North-star journey

```text
Screen → Intake → Explain → Route → Travel → Heal → Follow-up
```

## Problem

The product brief identifies three connected gaps:

1. many people lack convenient specialist access and point-of-care diagnostics;
2. medical-tourism services are fragmented across hospitals, coordinators,
   travel, and follow-up;
3. community preventive screening is not connected to structured clinical intake
   and longitudinal care.

The supplied market figures are product-brief inputs. They require source-backed
verification before appearing in public marketing or investor material.

## Solution

MediKiosk provides:

- calibrated and explainable risk-screening slots, beginning with CardioVision;
- voice, touch, and prescription/document intake in 8+ Indian languages;
- clinician-ready summaries and interoperable FHIR output;
- transparent specialist/hospital matching by condition, budget, location,
  language, insurance, travel, and verified availability;
- consent-based digital health passport and communication flows;
- drug-safety and follow-up support;
- optional Blender/3D education and explainability with accessible fallbacks.

## What the current repository proves

The current checkout is a local working prototype, not a production deployment.
It proves a CardioVision-centered intake vertical slice, local persistence,
clinician queue behavior, local ABDM-shaped flows, and deterministic mocks.

It does not prove live ABDM, PM-JAY, WhatsApp, hospital/EHR, payment, ambulance,
medical-tourism, or clinical-model performance. See `docs/INTEGRATIONS.md` and
`docs/STATUS.md`.

## What MediKiosk is not

- not an autonomous diagnostic system;
- not an EHR replacement;
- not a substitute for a clinician or emergency service;
- not a booking/payment/travel agent without verified providers and confirmation;
- not “fully offline” when Gemini/OpenAI adapters are configured;
- not allowed to claim FHIR compliance or model performance without external
  validation/evaluation evidence.

## Success measures

Measure each capability with a reproducible protocol:

- intake time and completion;
- clinical completeness against a reviewed rubric;
- language-specific speech accuracy;
- document/entity extraction quality;
- model discrimination and calibration;
- subgroup/safety performance;
- FHIR validation and destination acceptance;
- consent, purge, audit, and PHI safety;
- accessibility, offline recovery, and operational reliability.

Business metrics and market claims must be kept separate from clinical evidence.
