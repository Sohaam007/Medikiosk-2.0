# MediKiosk 2.0 — Team Directory

Read `docs/TEAM_CAPACITY.md` for the operating model, parallel lanes, and
capacity limits. These pages define the default scope for each named owner.

| Person | Profile |
|---|---|
| Soham | [Architecture, Backend, Clinical Safety](SOHAM.md) |
| Soumyadeep | [Product Experience and Frontend](SOUMYADEEP.md) |
| Swapnil | [ML/AI and CardioVision](SWAPNIL.md) |
| Pabitra | [QA, Security Verification, Release Operations](PABITRA.md) |
| Aditya | [Integrations, Synthetic Data, Workflow Reliability](ADITYA.md) |

## Review pairing

- Soham ↔ Soumyadeep: cross-review API/UI and scope decisions.
- Swapnil → Soham: clinical/model boundary review.
- Aditya → Soham: integration/PHI boundary review.
- Pabitra → everyone: evidence, security, reproducibility, and release gates.

## Competition launch packets

Start from the packet, not from an unbounded chat request:

| Owner | First packet | Follow-on packet |
|---|---|---|
| Soham | [F-006](../tasks/active/F-006-care-navigator-referral-outcomes.md) | [F-010](../tasks/active/F-010-seva-scope-claim-freeze.md) review and release claims |
| Soumyadeep | [F-002](../tasks/active/F-002-landing-page-theme.md) | F-011 evidence handoff |
| Swapnil | [F-001](../tasks/active/F-001-cardiovision-handoff-evidence.md) | [F-004](../tasks/active/F-004-cardiovision-model-evidence.md) |
| Pabitra | [F-011](../tasks/active/F-011-seva-release-evidence.md) | Evidence review for F-001–F-004 |
| Aditya | [F-003](../tasks/active/F-003-demo-reset-fixtures.md) | F-011 reset and failure-path evidence |

The active packet board is `docs/tasks/active/README.md`. The five lanes may
work in parallel only when their write surfaces are isolated and the packet's
reviewer is named.

Names are human ownership labels, not GitHub usernames. Add verified GitHub
handles to CODEOWNERS only after the team confirms them.
