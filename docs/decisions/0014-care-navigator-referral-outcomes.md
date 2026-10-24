# ADR 0014: Add Local Audited Referral Workflow Outcomes

> **Status:** Proposed
> **Date:** 2026-10-25
> **Author:** Soham
> **Reviewers:** Soumyadeep, Pabitra

## Context

The current CardioVision referral endpoint returns local, non-binding doctor and
package candidate IDs, but does not preserve the subsequent human workflow. The
Product Scale roadmap needs a care navigator view that can record whether a
candidate was reviewed, contacted, attended, or declined without claiming a
clinical or treatment outcome.

The current repository has no referral-outcome entity, repository port, service,
API contract, or persistence table. Adding this capability crosses domain,
service, API, audit, and database boundaries and therefore requires a durable
decision before implementation.

## Decision

MediKiosk will add a local, clinician-controlled referral workflow outcome
capability with these statuses:

```text
recommended → reviewed → contacted → attended | declined
```

The first implementation will:

1. Store one current workflow record per referral candidate and session.
2. Permit only clinician roles to create and transition records.
3. Enforce transitions in deterministic domain policy.
4. Record every creation and transition through the append-only audit trail.
5. Expose only opaque session/referral/candidate identifiers and workflow
   metadata; no names, phone numbers, diagnoses, notes, or treatment outcomes.
6. Keep the capability local/offline and provider-free.

The status `attended` means the workflow records that attendance was reported or
marked by an authorized operator. It does not mean treatment occurred, that a
clinical outcome was achieved, or that a provider confirmed capacity.

Critical-veto sessions remain outside routine referral outcome tracking. A
critical safety path must be handled by the existing veto/emergency workflow,
not converted into a routine referral record.

## Persistence boundary

The active repository currently bootstraps local development tables with
SQLAlchemy `create_all`; no migration directory is present. This feature adds a
dedicated ORM table and keeps the existing local bootstrap behavior. A future
production deployment must introduce a migration-controlled lifecycle before
using this table outside the prototype environment.

No external provider, notification, booking, payment, hospital-capacity, or
patient-facing automation is added.

## Alternatives considered

### Store outcome state on `SessionState`

Rejected. A session can have multiple candidate doctors/packages, and widening
the root session contract would conflate referral workflow with intake state and
make history difficult to audit.

### Store free-text navigator notes

Rejected for the first slice. Free text creates an uncontrolled PHI channel and
would require retention, redaction, access, and review policy before it can be
safe.

### Send messages when a candidate is contacted

Rejected. Communications require consent, templates, delivery receipts, retry,
opt-out, escalation, and a reviewed provider boundary. This ADR records workflow
state only.

### Infer outcomes from screening or queue events

Rejected. Screening is not diagnosis, and workflow events cannot prove a
patient's treatment or clinical outcome.

## Consequences

### Positive

- Care navigation can preserve the next human action without pretending to book
  care or prove treatment success.
- Status transitions become deterministic, testable, and auditable.
- The capability remains local and reversible while provider integrations stay
  deferred.
- The domain contract is separate from `SessionState` and CardioVision scoring.

### Negative

- A new persistence table and generated API contract are required.
- The local bootstrap path is sufficient for the prototype but not a production
  migration strategy.
- The first slice cannot carry navigator notes, messaging, or outcome detail.

## Rollback and promotion

- Disable the referral outcome routes and retain the existing non-binding
  CardioVision referral endpoint.
- Remove the new ORM table only through an explicit forward migration in a
  future migration-controlled environment; do not manually mutate production.
- Do not promote `attended` or any workflow status into a clinical outcome claim.
- Do not promote this local capability to a provider-connected routing or
  messaging integration without a new contract, adapter, consent, and evidence
  review.
