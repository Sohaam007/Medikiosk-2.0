# MediKiosk 2.0 — Design System Direction

The frontend is moving from scattered utility styling to a custom,
shadcn-compatible component system. The goal is a recognizable clinical product,
not a default Tailwind starter.

## Design principles

- Calm, trustworthy, and legible before decorative.
- Large touch targets and strong focus states for kiosk use.
- Dense, scannable data hierarchy for clinicians.
- High-contrast emergency states without alarm fatigue.
- Progressive enhancement for 3D, animation, audio, and network features.
- Same design language across landing, kiosk, clinician, passport, and routing.

## Token families

Define tokens in CSS/custom theme files before using them in components:

- semantic colors: background, surface, text, muted, border, primary, accent,
  success, warning, emergency, cardio;
- typography: display, heading, body, label, mono;
- spacing and layout grid;
- radius and elevation;
- motion duration/easing and reduced-motion behavior;
- kiosk target sizes and clinician density modes.

## Component layers

```text
components/ui/       shadcn-compatible primitives
components/layout/   shells, navigation, banners, responsive containers
components/<domain>/ product components and clinical states
features/<capability>/ data, hooks, UI, and acceptance tests
pages/               route-level composition only
```

## Required states

Every data-backed component must design:

- loading/skeleton;
- empty/no-result;
- offline/unavailable;
- validation error;
- provider failure;
- success/confirmation;
- clinician review or disclaimer state where applicable.

## Clinical UI rules

- Do not use color alone for severity.
- Keep “screening support only” visible next to CardioVision results.
- Make emergency/veto actions visually and semantically distinct from commerce.
- Never show a local mock as a live provider confirmation.
- Never place unredacted PHI in demo screenshots or sample content.
