# ADR 0010: Freeze and Disposition Legacy Runtime Trees

> **Status:** Accepted  
> **Date:** 2026-10-22  
> **Author:** Soham  
> **Reviewers:** Soumyadeep, Pabitra

## Context

The repository contains `backend/`, `core/`, `server/`, and `kiosk/` trees that
look like plausible runtime implementations but are not the active packaged
runtime. This creates import confusion and makes agents implement against stale
paths. The active runtime is `src/medikiosk/` plus `frontend/`.

## Decision

1. New runtime code must not be added to the legacy trees.
2. The detailed architecture backlog is archived; the active future map is
   `docs/ARCHITECTURE_BACKLOG.md` and the active sequence is `docs/ROADMAP.md`.
3. A separate migration task will classify each legacy tree as archive, delete,
   or migration source using parity evidence before physically removing code.
4. No legacy code is deleted in the documentation change alone, so the current
   working prototype remains reversible.

## Consequences

- Agents have one active backend and one active frontend path.
- The repository remains temporarily larger until the migration task is complete.
- Any legacy-tree reactivation requires a new ADR or explicit migration task.
