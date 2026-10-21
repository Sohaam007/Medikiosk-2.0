# ADR 0012: Add Clinical and Regulatory Readiness Before Pilot

> **Status:** Accepted
> **Date:** 2026-10-22
> **Author:** Soham
> **Reviewers:** Swapnil, Pabitra

## Context

CardioVision and future screening models may influence clinical review or
referral prioritization. The repository currently has strong technical safety
boundaries but no regulatory classification, intended-use approval, clinical
advisor sign-off, or pilot-site governance.

## Decision

Before any real-patient pilot, the project must complete the readiness work in
`docs/CLINICAL_REGULATORY.md`, including qualified external review of intended
use, clinical workflow, privacy/data handling, model evidence, and applicable
regulatory obligations.

The engineering team may prepare evidence and synthetic evaluations, but may not
self-certify clinical validation, regulatory classification, or patient safety.

## Consequences

- Prototype and SEVA demo work can continue with synthetic data and visible
  screening-only language.
- Pilot and production work gains an explicit external-review gate.
- Marketing and investor claims must distinguish technical capability from
  clinical/regulatory approval.
