# MediKiosk 2.0 — Clinical and Regulatory Readiness

This document is a readiness plan, not legal or medical advice. The team must
obtain qualified clinical, regulatory, privacy, and deployment review before
pilot use with real patients.

## Why this exists

CardioVision and future screening models may influence clinician review or
referral prioritization. That creates a responsibility to assess the applicable
clinical-software and medical-device obligations before a pilot, even when the
product uses screening-only language.

## Current position

- The repository is a local prototype.
- CardioVision is screening support, not diagnosis.
- No regulatory classification has been determined.
- No clinical validation or human-subjects approval is claimed.
- No real-patient deployment is authorized by this repository.

## Required discovery work

| Work item | Accountable | Required evidence |
|---|---|---|
| Define intended use and user population | Soham | Approved intended-use statement |
| Identify whether any model output changes clinical workflow | Soham + Swapnil | Data-flow and decision-impact map |
| Obtain qualified regulatory opinion | Soham | Written external assessment; not an internal assumption |
| Define clinical review and escalation policy | Soham | Signed clinical workflow policy |
| Define data protection/consent/retention review | Soham + Aditya | Privacy and data-flow assessment |
| Usability review with health workers | Soumyadeep + Pabitra | Dated protocol, findings, remediation log |
| Model validation plan | Swapnil | Evaluation protocol, approved data provenance, model card |
| Pilot-site and hospital governance | Soham + Aditya | Named partner, owner, training and incident process |

## Safety boundaries before pilot

- No diagnosis or treatment claims.
- No autonomous emergency or commercial action.
- Clinician review for screening and routing.
- Explicit uncertainty/missing-data behavior.
- Audit trail for consent, overrides, sharing, and purge.
- Incident response and rollback owner.
- Approved data-processing and provider agreements.
- No live patient traffic in demo or development environments.

## Promotion gates

```text
prototype
→ synthetic evaluation
→ clinician workflow review
→ regulatory/privacy assessment
→ approved de-identified or pilot data
→ supervised pilot
→ monitored production consideration
```

The team may prepare the evidence package, but a qualified external reviewer must
own the final clinical/regulatory decision.
