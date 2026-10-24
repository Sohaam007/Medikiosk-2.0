# F-002 — Landing Page and Kiosk Theme

## Identity

- Feature: Custom shadcn-compatible landing page and kiosk theme
- Phase: Track A — SEVA Demo Release
- Owner: Soumyadeep
- Reviewer: Soham
- Branch: `feat/f002-landing-page-theme`

## User outcome

Patients, clinicians, and judges can understand the current MediKiosk journey
through a calm, accessible, touch-friendly interface that distinguishes the
working local prototype from future product-scale capabilities.

## Current evidence

- Runtime: React 19 + TypeScript + Vite in `frontend/`.
- Active views: `KioskIntakeView.tsx`, `ClinicianQueueView.tsx`.
- Existing visual guidance: `docs/DESIGN_SYSTEM.md` and
  `docs/FRONTEND_HANDOFF.md`.
- API source of truth: generated client under `frontend/src/client/`.

## Scope

- Allowed paths: `frontend/`, visual/a11y tests, `docs/DESIGN_SYSTEM.md`,
  `docs/DEMO_EVIDENCE.md`, and this packet.
- Forbidden paths: backend contracts without Soham approval, handwritten API
  types, live-provider claims, clinical wording changes without review, and
  legacy UI trees.
- Out of scope: new backend features, payment/booking UX, real provider
  delivery, and Product Scale passport/care-navigator UI.

## Contract and safety

- Consume generated API types only; regenerate after any approved API change.
- Keep screening-only, clinician-review, local/mock, and offline language visible.
- Design loading, empty, offline, validation-error, provider-failure, success,
  and disclaimer states for data-backed components.
- Do not use color alone for severity; preserve keyboard and touch access.
- Never show a local candidate as a booking, capacity, or provider confirmation.

## Acceptance criteria

- [ ] Landing/pitch surface explains the complete journey and current scope.
- [ ] Kiosk and clinician surfaces share documented tokens and responsive rules.
- [ ] Primary touch targets and focus states meet the project accessibility bar.
- [ ] CardioVision explanation retains model/version/disclaimer visibility.
- [ ] Offline/auth failure is visible and cannot look like provider success.
- [ ] Screenshots contain only synthetic data and are ready for Pabitra's evidence
      package.

## Verification

- `cd frontend && npm run lint`
- `cd frontend && npm run build`
- Manual keyboard, touch-target, responsive, reduced-motion, and offline smoke.
- Review clinical wording and API/client alignment with Soham.

## Rollback

Revert visual changes independently; preserve the existing kiosk and clinician
flow. Remove any UI state that cannot be backed by an implemented contract.

## Handoff

Return a visual change summary, screenshots or redacted references, accessibility
notes, and known UI limitations to Soham and Pabitra.
