# MediKiosk 2.0 — Canonical Product Context

**Role:** stable domain context and product vocabulary.

This document explains what the project is trying to become and what the current
repository actually proves. It is not a substitute for code, tests, or an ADR.
When this document conflicts with executable behavior, code and tests win and
the discrepancy must be recorded in `docs/STATUS.md`.

## Product identity

MediKiosk 2.0 is a unified health-journey platform for Indian healthcare
settings. It begins at the hospital or community front door and turns a patient
interaction into structured, reviewable, consent-aware clinical information.

The long-term journey is:

```text
Screen → Intake → Explain → Route → Travel → Heal → Follow-up
```

The current repository implements a smaller vertical slice:

```text
CardioVision screen → multilingual intake → document capture → clinician queue
→ local summary/FHIR-shaped output → local referral candidates
```

The current implementation is a working prototype, not a production clinical
deployment and not evidence of live partner connectivity.

## Problem statement

The product brief supplied for this project frames three connected gaps in
India:

1. **Specialist access:** hundreds of millions of people lack convenient access
   to specialists; the brief cites roughly one cardiologist per 50,000 people
   and diagnostics gaps across primary-care facilities.
2. **Medical-tourism fragmentation:** the brief describes a large but
   disconnected medical-tourism sector without a unified patient journey.
3. **Preventive screening:** community-level preventive screening is sparse and
   disconnected from intake, referral, and follow-up.

These figures are product-brief inputs, not independently verified claims in
this repository. External marketing, investor, grant, or clinical documents must
attach sources before publishing them.

## Product thesis

MediKiosk should reduce the gap between a patient's first interaction and a
clinician's next safe decision by combining:

- preventive risk screening with calibrated, explainable models;
- voice, touch, and document-based intake in 8+ Indian languages;
- structured clinical summaries and interoperable health records;
- clinician-reviewed specialist and hospital routing;
- consent-based patient engagement through digital channels;
- follow-up continuity instead of a one-time kiosk transaction.

The system is a clinical workflow and interoperability layer. It is not an
autonomous diagnostician, not an emergency dispatcher without verified
infrastructure, and not a replacement for a hospital EHR.

Delivery is split into two tracks:

- **SEVA Demo Track:** a stable local CardioVision-to-clinician vertical slice
  using synthetic data and visible mock/offline boundaries.
- **Product Scale Track:** community screening campaigns, multi-disease model
  slots, care navigation, digital passport, follow-up, provider integrations,
  optional 3D education, and production operations.

The five-person ownership model is defined in `docs/TEAM_CAPACITY.md`; the demo
track is frozen before product-scale work changes its contracts or behavior.

Practical expansions include batch/community screening, a care navigator
workspace, referral outcome tracking, consented caregiver access, medication-
safety review, a multilingual education library, and a zero-PHI operations
health console.

## Product surfaces

| Surface | Primary user | Current state |
|---|---|---|
| Landing page | Patient, hospital, partner, reviewer | Existing app shell; full product landing experience is a planned UI workstream. |
| Patient kiosk | Patient, relative, caregiver, community health worker | Active React view with language, intake, document, service, and token flow. |
| CardioVision | Patient and clinician | Active bounded cardiovascular screening and referral slice. |
| Clinician console | Clinician, intake desk, hospital operator | Active queue and review view with local/demo data paths. |
| Digital health passport | Patient and authorized care team | Product target; not implemented as a complete capability. |
| Medical-tourism routing | Patient, coordinator, hospital partner | Product target; only a narrow local cardiology candidate matcher exists. |
| Blender/3D explanation | Patient, clinician, demonstrator | Product target; Blender asset pipeline is not yet present in the active runtime. |

## Capability boundaries

### Screening

Screening estimates risk or identifies a review signal from structured inputs. It
must expose model/version metadata, explanations, missing-input behavior, and a
clinician-review boundary. A screening result must never be described as a
diagnosis.

### Intake

Intake gathers patient or proxy-reported information through voice, touch, and
documents. It should preserve source and confidence metadata and make proxy
informant status explicit.

### Explainability

Explainability is an aid to understanding model inputs and output, not a claim
that a model has discovered clinical causality. Visuals must distinguish model
contribution from medical advice.

### Routing

Routing ranks eligible options using explicit constraints such as condition,
specialty, language, location, budget, insurance, and verified availability.
Recommendations require human review until real partner data, safety rules, and
operational ownership are proven.

### Travel and medical tourism

Travel assistance may organize options and requirements. It must not promise a
medical outcome, issue a visa, buy a ticket, book treatment, or claim capacity
without a verified partner and an explicit confirmation step.

### Follow-up

Follow-up is a consent-based care-plan and communication workflow. It must have
opt-out, delivery status, retry, audit, and escalation semantics before it sends
anything to a patient.

## Product vocabulary

| Term | Meaning in this repository |
|---|---|
| CardioVision | The bounded cardiovascular screening adapter and its result contract. |
| Screening | A risk/flag estimate used to support review; never a diagnosis. |
| Intake session | The bounded interaction identified by an opaque UUID. |
| Informant | The person providing history: patient, relative, or caregiver. |
| Clinician review | A human decision point required before consequential clinical or commercial action. |
| Mock adapter | Deterministic/local implementation used for development and tests. |
| Sandbox adapter | External provider integration against a non-production environment. |
| Production adapter | External provider integration with approved credentials, contracts, monitoring, and rollback. |
| FHIR-shaped | A locally generated structure that resembles FHIR but has not yet been proven by an external validator or destination system. |
| Live capacity | Availability obtained from an authenticated, current provider source; local fixtures are not live capacity. |
| PHI egress | Any path that can send patient-identifying or clinical data outside the local process or approved deployment boundary. |

## Safety and claims policy

The application may claim only what is supported by executable evidence. A UI
card, fixture, seed record, mock gateway, or local SSE event is not evidence of a
live integration.

Before using a phrase such as “integrated,” “real-time,” “FHIR-compliant,”
“ABDM-connected,” “WhatsApp-enabled,” “production-ready,” or “>90% AUC,” record:

1. the exact implementation path;
2. the environment and credentials used;
3. the test or evaluation command;
4. the date and result;
5. limitations and failure behavior.

## New-feature decision test

An addition belongs in this project only if it improves at least one of:

- access to safe specialist review;
- preventive screening reach;
- quality or speed of structured intake;
- interoperability and continuity of care;
- patient understanding and engagement;
- operational safety and auditability.

Every addition must also identify its data boundary, clinical owner, rollback
behavior, offline behavior, and verification evidence.

## Visual explanation and assistant boundary

Product-scale explanation uses reusable body-system scenes rather than one
generated 3D mesh per disease. The supported progression is:

```text
body map → generic anatomy education → approved screening overlay
→ patient-specific imaging only after a separate validated workflow
```

Blender assets are educational/progressive-enhancement artifacts. Clinical
anatomy is assembled from licensed, clinician-reviewed reference geometry and
deterministic Blender Python scripts; a text-to-3D generator is not accepted as
medical truth. The web runtime must retain a static 2D/text fallback.

The AI assistant is a bounded language and workflow layer. It may ask approved
questions, translate, read aloud, and explain validated structured output. It
must not diagnose, prescribe, invent evidence or anatomy, override red flags,
select a provider, book, pay, or dispatch emergency resources. See
`docs/3D_AND_ASSISTANT_ARCHITECTURE.md` and ADR 0013.
