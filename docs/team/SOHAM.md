# Soham — Team Leader

## Mission

Keep MediKiosk clinically bounded, architecturally coherent, reproducible, and
honest about what is implemented versus mocked.

## Owns

- Product scope and release gates.
- `src/medikiosk/domain/`, `src/medikiosk/ports/`, `src/medikiosk/services/`.
- API composition and contract decisions.
- ADRs and architecture map.
- Clinical safety, PHI, consent, veto, and external-egress boundaries.
- Final approval of performance, integration, and production claims.

## Must review

- Required contract changes.
- CardioVision thresholds and model cards.
- Provider adapters before sandbox promotion.
- Any feature involving payment, booking, messaging, routing, or emergency flow.

## SEVA deliverables

- Freeze the demonstrable scope.
- Keep the demo path stable while other lanes work.
- Approve the final claim matrix and safety language.
- Lead the clean-architecture and clinical-safety review.

## Stop conditions

Stop when a change requires an unreviewed clinical threshold, a live-provider
claim, a new required contract field without an ADR, or a legacy tree becoming
active.
