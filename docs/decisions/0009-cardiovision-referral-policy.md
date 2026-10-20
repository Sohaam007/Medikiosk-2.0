# ADR 0009: Add a non-binding CardioVision referral policy

## Decision

MediKiosk 2.0 adds a pure `match_cardiovascular_referral` policy and a
separate `POST /api/screening/cardiovascular/referral` endpoint. The policy
returns stable doctor and cardiac-package candidate IDs from local fixtures.
It never selects a doctor, purchases a package, allocates emergency resources,
or claims live capacity.

A positive CAD or vessel screening label produces an `urgent` cardiology review
recommendation. A low-risk result produces no automatic referral. Emergency
disposition remains the responsibility of the server-side veto engine and is
not inferred from a model probability alone.

## Rationale

The SEVA plan's next step after screening is “Connect,” but the existing UI
recommendation was client-side and not backed by availability or package
catalogue data. This small boundary makes the recommendation deterministic,
explainable, and testable without widening session persistence or pretending
that local fixtures are a national hospital marketplace.
