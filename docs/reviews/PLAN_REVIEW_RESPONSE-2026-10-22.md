# Plan Review Response — October 22, 2026

## Source

Reviewed the external Antigravity assessment at:

```text
C:\Users\Acer\.gemini\antigravity-cli\brain\e990bfa4-8d19-44f1-9b55-693ce55740f9\MEDIKIOSK_PLAN_REVIEW.md
```

The assessment rated the documentation `4/5` overall and identified scope/team
capacity, legacy trees, demo evidence, agent-process overhead, model evidence,
and regulatory readiness as the main risks.

## Decisions adopted

1. Replace the outdated two-person plan with a five-person ownership model:
   Soham (leader), Soumyadeep (co-lead), Swapnil (ML/AI), Pabitra (QA/release),
   and Aditya (integrations/data).
2. Split delivery into a frozen **SEVA Demo Track** and a larger **Product Scale
   Track**.
3. Keep the demo path local, synthetic, repeatable, and honest about mocks.
4. Archive the detailed architecture backlog and retain a concise future
   capability map.
5. Add a legacy-tree disposition ADR without deleting code until parity and
   migration evidence exist.
6. Add a clinical/regulatory readiness gate before real-patient pilot use.
7. Add a demo evidence plan for screenshots, recording, clean-clone proof, and
   claim review.
8. Expand the product roadmap with community screening, care navigation,
   referral outcome tracking, caregiver access, medication safety, education,
   operations health, and evidence dashboards.

## Deliberately not adopted as current claims

- Clinical validation or `>90% AUC`.
- Live ABDM, PM-JAY, WhatsApp, payment, hospital/EHR, ambulance, travel, or
  medical-tourism connectivity.
- Regulatory classification or approval.
- Production readiness.

Those remain explicit evidence gaps in `docs/STATUS.md`, `docs/INTEGRATIONS.md`,
`docs/UNVERIFIED.md`, and `docs/CLINICAL_REGULATORY.md`.
