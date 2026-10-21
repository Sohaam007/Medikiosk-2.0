# MediKiosk 2.0 — Ownership and Agent Roles

This file defines who reviews which surface and how AI agents divide work. It
does not replace GitHub CODEOWNERS or a task tracker; it prevents agents from
guessing ownership.

## Human ownership currently recorded in the repository

| Owner | Primary areas | Review responsibility |
|---|---|---|
| Soham | backend architecture, domain, ports, services, adapters, docs, security | contracts, invariants, provider boundaries, production claims |
| Soumyadeep | frontend, API route integration, integration tests, UX | generated client alignment, accessibility, browser behavior |

If a change crosses both areas, one person writes and the other reviews. Do not
create two independent implementations of the same file or contract.

## Active path ownership

| Path | Default owner | Required reviewer |
|---|---|---|
| `src/medikiosk/domain/` | Backend/domain | Backend architecture reviewer |
| `src/medikiosk/ports/` | Backend architecture | Affected integration owner |
| `src/medikiosk/services/` | Backend/application | Backend architecture reviewer |
| `src/medikiosk/adapters/` | Backend/integration | Security and affected provider reviewer |
| `src/medikiosk/api/` | Backend/API | Frontend/integration reviewer when contract changes |
| `frontend/` | Frontend | Backend/API reviewer when SDK/API changes |
| `tests/` | Feature owner | Independent QA/reviewer |
| `models/`, `eval/` | ML/model owner | Clinical-safety and data reviewer |
| `blender/` and 3D frontend | 3D/UI owner | Frontend performance/accessibility reviewer |
| `docs/` | Architecture owner | Affected domain owner |
| `.github/`, Docker, deployment | Release/security owner | Backend architecture reviewer |

## Role-based agents

### Architect

Owns boundaries, ADRs, contracts, dependency direction, migration sequencing,
and the regression map. Must return an impact map before implementation.

### Backend agent

Owns pure domain rules, ports, services, adapters, routes, persistence, and
backend tests. Must keep routes thin and must never place provider code in the
domain.

### Frontend agent

Owns React features, custom shadcn-compatible primitives, theme tokens,
generated client usage, responsive behavior, kiosk touch targets, and a11y.
Must not manually duplicate backend contracts.

### ML agent

Owns model registry, preprocessing, calibration, evaluation, model cards,
thresholds, explainability payloads, and rollback metadata. Must not claim
clinical performance without a reproducible report.

### Blender/3D agent

Owns `.blend` scenes, materials, export scripts, GLB manifests, asset validation,
and frontend 3D fallback behavior. Must not use real patient likenesses or block
the primary UI on GPU capability.

### Integrations agent

Owns ABDM, FHIR/EHR, PM-JAY, WhatsApp/SMS, payments, pharmacy, travel, and
hospital-provider adapters. Each integration starts as a mock and has timeout,
retry, idempotency, signature, audit, and rollback rules.

### Security/privacy agent

Owns PHI review, auth/role checks, secret handling, upload validation, external
egress review, threat-model updates, and security gates.

### QA agent

Owns regression, contract, invariant, E2E, accessibility, visual, offline, and
clean-clone checks. The QA agent reports actual commands and exit codes.

### Release/operations agent

Owns versioning, CI, Docker, migrations, deployment, observability, backups,
runbooks, rollback, and release evidence.

## Assignment rules

- One task packet has one accountable owner.
- A task may have multiple reviewers but not multiple uncoordinated writers.
- A cross-domain contract change needs an ADR and both domain owners' review.
- A new provider needs integration and security review before sandbox use.
- A model change needs ML and clinical-safety review before production claims.
- A UI change affecting clinical wording needs product/clinical review.

## Escalation

If a decision is blocked for more than one working session, write the proposed
options and risks in an ADR or task note. Do not silently choose a provider,
clinical threshold, data-retention rule, or production deployment target.
