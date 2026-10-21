# ADR 0011: Five-Person Two-Track Delivery Model

> **Status:** Accepted  
> **Date:** 2026-10-22  
> **Author:** Soham  
> **Reviewers:** Soumyadeep, Swapnil, Pabitra, Aditya

## Context

The product vision includes screening, intake, explainability, routing, travel,
follow-up, external integrations, and production operations. A two-person plan
would either overpromise the SEVA submission or prevent useful parallel work. The
team now has five named contributors with Soham as leader and Soumyadeep as
co-lead.

## Decision

1. Run a frozen **SEVA Demo Track** for a reliable local CardioVision-to-
   clinician vertical slice.
2. Run a separate **Product Scale Track** for multi-disease screening,
   community campaigns, care navigation, provider integrations, digital passport,
   follow-up, optional 3D, and production operations.
3. Assign ownership as documented in `docs/TEAM_CAPACITY.md`:
   - Soham: architecture/backend/clinical safety;
   - Soumyadeep: product/frontend/demo experience;
   - Swapnil: ML/AI/CardioVision;
   - Pabitra: QA/security verification/release;
   - Aditya: integrations/synthetic data/workflow reliability.
4. The Demo Track may not be destabilized by Product Scale work without a scope
   exception, regression evidence, and Soham/Soumyadeep approval.

## Consequences

- The team can work in parallel on isolated surfaces.
- The submission remains credible and repeatable.
- Product work continues without presenting planned integrations as current.
- Every task has a human owner even when AI agents perform implementation.
