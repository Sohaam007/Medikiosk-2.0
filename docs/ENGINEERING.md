# MediKiosk 2.0 — Engineering Standards

These standards are intentionally specific to this clinical, AI-assisted,
multi-surface project.

## Python

- Target Python `3.11.9`; use complete type annotations and strict mypy.
- Use Ruff with the repository's `pyproject.toml` settings and 100-character
  lines.
- Use `snake_case` for functions/variables, `PascalCase` for types, and
  `UPPER_CASE` for constants.
- Use `structlog` for operational logs; do not use `print()` in runtime code.
- Catch specific exceptions and translate provider errors at adapter boundaries.
- Use timezone-aware UTC datetimes and injected clocks/IDs in pure domain logic.
- Keep mutable state inside services/adapters; do not introduce hidden module
  globals for clinical state.

## Domain and services

- Pure domain functions must be deterministic for identical inputs.
- Inject time, randomness, UUIDs, network clients, repositories, and model
  providers.
- Keep provider-specific request/response types inside adapters.
- Use Pydantic contracts at boundaries; validate before use.
- Do not hide clinical policy inside an API route or React component.
- Do not create a parallel contract when an existing one can be extended safely.

## API

- Routes validate input, enforce auth/role/consent, call a service, and map the
  response. They do not orchestrate multi-step business policy inline.
- Use stable error codes and PHI-scrubbed messages.
- Explicitly document public versus authenticated routes.
- Bound body, file, queue, SSE, and provider response sizes.
- Add idempotency for webhooks, payments, notifications, and external pushes.
- Use timeouts and bounded retries for all provider calls.

## LLM and model calls

- Prompts use parameterized templates; never concatenate raw patient text into a
  system prompt or log prompt/response content.
- Every LLM call is stateless across sessions.
- Validate structured output against a Pydantic schema before using any field.
- Enforce input/output token ceilings and provider timeouts.
- Record model/provider/version and outcome metadata without recording PHI.
- Model output is advisory until a clinician/safety policy explicitly accepts it.

## Frontend

- Use the generated API client for backend calls.
- Keep server state, UI state, route state, form state, and offline queue state
  separate.
- Put reusable primitives in `frontend/src/components/ui/`; put product behavior
  in feature folders.
- Use semantic HTML, keyboard support, visible focus, accessible labels, and
  minimum 48px kiosk touch targets.
- Every network-backed feature needs loading, error, offline, empty, and success
  states. Offline preview must be visibly labeled.
- Respect reduced-motion and low-power/device capability fallbacks.

## Data and persistence

- Use SQLAlchemy parameterized queries/ORM; never interpolate SQL.
- Use migrations for production schema changes; local table creation is a dev
  convenience only.
- Store opaque IDs and hashes in audit logs; never raw clinical payloads.
- Treat uploaded files, OCR text, transcripts, and model payloads as sensitive.
- Define retention and purge behavior for every new persisted field.

## Dependencies and generated files

- Pin runtimes and keep lockfiles updated in the same change as dependency edits.
- A new dependency requires an ADR, license/security review, and reproducibility
  check.
- Do not hand-edit generated OpenAPI or TypeScript client files.
- Regenerate and review generated diffs after API schema changes.
