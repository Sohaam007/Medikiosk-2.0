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

Update the matching row in `docs/FEATURES.md` in the same PR. Do not use the
historical files under `docs/tasks/` as an active backlog.
