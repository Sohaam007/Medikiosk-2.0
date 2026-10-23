# MediKiosk 2.0 — Active Feature Register

**Role:** the small, current index of capabilities that the team is actively
building, verifying, reviewing, or intentionally deferring.

This is an index, not a replacement for task packets, architecture docs, tests,
or ADRs. A row may claim `Done` only when its implementation, evidence, and
required checks are recorded in the linked task packet or PR.

## Status vocabulary

```text
Proposed → Ready → In Progress → Review → Done
                         ↘ Blocked
Proposed/Ready/In Progress → Deferred
```

## Active register

| ID | Capability | Track | Owner | Required reviewer | Status | Task packet / evidence |
|---|---|---|---|---|---|---|
| F-001 | CardioVision screening to clinician handoff | SEVA demo | Swapnil | Soham + Pabitra | Evidence pending | `docs/SEVA_SUBMISSION.md`, `docs/DEMO_EVIDENCE.md` |
| F-002 | Custom shadcn-compatible landing page and kiosk theme | SEVA demo | Soumyadeep | Soham | Ready | Create `docs/tasks/active/F-002-*.md` before implementation |
| F-003 | Deterministic synthetic demo reset and failure fixtures | SEVA demo | Aditya | Pabitra + Soham | Ready | Create `docs/tasks/active/F-003-*.md` before implementation |
| F-004 | CardioVision model card, evaluation, and limitation evidence | SEVA demo | Swapnil | Soham + Pabitra | Ready | `docs/MODEL_GOVERNANCE.md` |
| F-005 | Community screening campaign mode | Product scale | Aditya | Soham + Pabitra | Proposed | Create a task packet after SEVA demo freeze |
| F-006 | Care navigator workspace and referral outcome tracking | Product scale | Soham | Soumyadeep + Pabitra | Proposed | Create a task packet after SEVA demo freeze |
| F-007 | Medication-safety review and multilingual education library | Product scale | Soham | Swapnil + Pabitra | Proposed | Create a task packet after SEVA demo freeze |
| F-008 | Blender/GLB patient explanation assets with low-power fallback | Product scale | Swapnil | Soumyadeep + Pabitra | Proposed | `docs/BLENDER_PIPELINE.md` |

## Rules for agents

1. Find or create the feature row before implementation.
2. Create a bounded packet from `docs/templates/FEATURE.md` under
   `docs/tasks/active/` before making a non-trivial change.
3. Put the human owner, reviewer, branch, allowed paths, acceptance criteria,
   verification commands, rollback, and documentation owner in that packet.
4. Update only the canonical documentation owner for facts that changed. Do not
   copy the same status into several documents.
5. Update the row's status and PR link in the same PR as the implementation.
6. Move completed packets to an explicitly tracked archive only when their
   acceptance evidence is complete; do not silently delete history.

## Definition of done

A feature is `Done` only when:

- the acceptance criteria are checked;
- focused and downstream checks have passed;
- generated artifacts are synchronized when applicable;
- security, PHI, consent, and external-egress boundaries were reviewed;
- the canonical docs were updated;
- the PR was approved and merged by a human owner;
- remaining limitations are recorded.
