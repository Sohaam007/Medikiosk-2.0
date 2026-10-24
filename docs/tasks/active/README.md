# Active Feature Task Packets

This directory contains the bounded task packets for work that is currently
ready, in progress, or under review.

Create each packet from:

```text
docs/templates/FEATURE.md
```

Use the naming form:

```text
<feature-id>-<short-slug>.md
```

Examples:

```text
F-002-landing-page-theme.md
F-003-demo-reset-fixtures.md
```

The packet is the work contract for the agent. It must name one human owner and
one reviewer, define allowed and forbidden paths, state the user outcome, list
acceptance criteria, and record exact verification commands.

Update the matching row in `docs/FEATURES.md` in the same PR. Do not use
historical material outside the repository as an active backlog.

## Team launch board

These packets are the bounded starting points for the competition work window.
Each owner should work only inside the packet's allowed paths and record exact
verification evidence before handing off to the named reviewer.

| Packet | Owner | Reviewer | Depends on | First useful outcome |
|---|---|---|---|---|
| [F-010](F-010-seva-scope-claim-freeze.md) | Soham | Soumyadeep + Pabitra | None | Frozen claims and Track A acceptance gate |
| [F-001](F-001-cardiovision-handoff-evidence.md) | Swapnil | Soham + Pabitra | F-010 claim boundary | Reproducible CardioVision handoff evidence |
| [F-002](F-002-landing-page-theme.md) | Soumyadeep | Soham | F-010 claim boundary | Accessible kiosk/clinician visual system and demo polish |
| [F-003](F-003-demo-reset-fixtures.md) | Aditya | Pabitra + Soham | F-010 claim boundary | Resettable synthetic demo and visible failure fixtures |
| [F-004](F-004-cardiovision-model-evidence.md) | Swapnil | Soham + Pabitra | F-001 model outputs | Model card, manifest, limitations, and offline evaluation record |
| [F-006](F-006-care-navigator-referral-outcomes.md) | Soham | Soumyadeep + Pabitra | F-010 scope freeze | Local audited referral workflow status API |
| [F-011](F-011-seva-release-evidence.md) | Pabitra | Soham + affected owner | F-001–F-004 stabilization | Clean-clone, smoke, regression, and submission evidence |

### Cross-lane rules

- F-010 defines the frozen Track A claims; no lane may widen them silently.
- F-001 and F-004 may not publish clinical-performance claims without Soham
  safety review and Pabitra reproducibility evidence.
- F-002 must consume generated API types and must not create handwritten API
  contracts.
- F-003 fixtures are synthetic only and must make provider boundaries visible.
- F-006 is Product Scale work and must not destabilize the frozen Track A path.
- F-011 is the release gate; a passing local test is not enough when screenshots,
  clean-clone proof, or human review evidence is missing.
