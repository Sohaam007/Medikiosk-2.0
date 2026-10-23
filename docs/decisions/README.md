# Architecture Decision Records

ADRs capture durable decisions that future agents must not silently reverse.
Routine implementation details belong in code, tests, or the task/PR record.

## Create an ADR when

- a cross-module contract changes;
- a dependency, provider, model, database, or deployment target is added;
- a security, consent, retention, or PHI boundary changes;
- a clinical threshold, veto, or commercial-flow rule changes;
- the active architecture or legacy-tree disposition changes.

## Process

1. Copy `0000-template.md` to the next number and a short slug.
2. State context, decision, alternatives, consequences, and rollback.
3. Mark `Proposed` until reviewed.
4. Implement only after the decision is accepted or explicitly approved for a
   bounded experiment.
5. Update the relevant canonical map/status/integration document.

## Index

| ADR | Title | Status |
|---|---|---|
| [0000](0000-template.md) | ADR template | Template |
| [0001](0001-clean-architecture-migration.md) | Clean architecture migration | Accepted |
| [0002](0002-zero-trust-edge-security.md) | Zero-trust edge security | Accepted |
| [0003](0003-ai-orchestrated-sdlc.md) | AI-orchestrated SDLC | Accepted |
| [0004](0004-add-ayush-codesystems.md) | AYUSH code systems | Accepted |
| [0005](0005-add-billing-fields-to-session-state.md) | Billing fields in session state | Accepted |
| [0006](0006-add-vitals-and-news2-fields-to-session-state.md) | Vitals and NEWS2 fields | Accepted |
| [0007](0007-add-phase3-domain-contracts.md) | Phase 3 domain contracts | Accepted |
| [0008](0008-cardiovision-boundary.md) | CardioVision screening port boundary | Accepted |
| [0009](0009-cardiovision-referral-policy.md) | Non-binding CardioVision referral policy | Accepted |
| [0010](0010-legacy-tree-disposition.md) | Freeze and disposition legacy runtime trees | Accepted |
| [0011](0011-five-person-two-track-delivery.md) | Five-person two-track delivery model | Accepted |
| [0012](0012-clinical-regulatory-readiness-gate.md) | Clinical and regulatory readiness gate | Accepted |
| [0013](0013-model-aware-explanation-and-assistant.md) | Separate clinical models, 3D explanations, and AI assistant | Proposed |

## Current decision rule

If an old ADR names a path that no longer exists, treat the decision intent as
historical context and verify the current implementation in
`docs/ARCHITECTURE.md`. Do not recreate stale paths merely because an old ADR
mentions them.
