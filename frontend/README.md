# MediKiosk 2.0 Frontend Guide

The active frontend is a React 19 + TypeScript + Vite application. It contains
two product surfaces: the patient/community kiosk and the clinician console.

## Runtime

- Node: `.nvmrc` → `24.19.0`.
- Package manager: npm with `package-lock.json`.
- Dev server: Vite on port `5173`.
- API proxy: `/api` → `http://127.0.0.1:8000` in `vite.config.ts`.
- Entry point: `src/main.tsx`.
- Root mode switcher: `src/App.tsx`.

## Setup and commands

From the repository root:

```bash
uv sync --frozen --extra dev
cd frontend
npm ci
npm run dev
```

Available commands:

```bash
npm run dev
npm run build
npm run lint
npm run format
npm run format:check
npm run generate-client
npm run preview
```

The Windows launcher at the repository root starts both backend and frontend:

```powershell
.\start_dev.bat
```

## Source map

```text
src/
├── App.tsx                 root mode switcher and shell
├── main.tsx                React bootstrap and API client setup
├── views/                  current kiosk and clinician workflow views
├── components/             shared/product components
├── hooks/                  browser, timer, queue, voice, and offline hooks
├── utils/                  language and clinical-question data
├── client/                 generated OpenAPI TypeScript client
├── index.css               Tailwind directives and global styles
└── App.css                 app-level styles
```

The current two large views are active but should be decomposed incrementally
into `src/features/` without changing behavior. Recommended future layout:

```text
src/
├── app/ routes and providers
├── pages/ route-level screens
├── features/ intake, screening, documents, queue, passport, follow-up
├── components/ui/ shadcn-compatible primitives
├── components/layout/ shells and navigation
├── components/three/ Blender/GLB viewers and fallbacks
├── services/ API-facing feature orchestration
├── stores/ client/offline state
└── styles/ tokens, theme, global styles
```

## API client contract

The backend is authoritative. After any route or Pydantic schema change:

```bash
uv run --extra dev python scripts/export_openapi.py
cd frontend
npm run generate-client
npm run build
```

Do not hand-edit `src/client/sdk.gen.ts`, `types.gen.ts`, or generated core
files. Use the generated functions and types instead of handwritten duplicates.

## Auth and fallback behavior

The client is configured in `src/main.tsx` and uses the local Vite proxy. The
current application may use local/offline fallbacks when the backend or token is
unavailable. A fallback must be visibly labeled as offline/demo and must not make
the user believe an external action succeeded.

Before adding a raw `fetch`, inspect the route's auth dependency. Add the Bearer
token consistently or explicitly document why the route is public. Do not store
real patient data in localStorage, IndexedDB fixtures, screenshots, or dev logs.

## UI rules

- Use semantic HTML and accessible labels.
- Maintain minimum 48px interactive targets for kiosk use.
- Support keyboard navigation and visible focus for clinician workflows.
- Provide loading, error, empty, offline, and success states.
- Respect reduced-motion and low-power fallbacks.
- Keep clinical warnings visible and do not hide screening-only disclaimers.
- Use design tokens instead of new arbitrary color literals.
- Put reusable UI primitives in `components/ui/`; put domain behavior in
  feature folders.

## CardioVision UI

`src/components/CardioVisionPanel.tsx` is the current cardiovascular surface.
It may show risk/explanation/referral candidates, but it must not:

- call a screening result a diagnosis;
- select a doctor or buy a package automatically;
- claim live hospital capacity;
- hide API failure behind a successful-looking state;
- block the full kiosk flow when CardioVision is unavailable.

Future Blender/Three.js work belongs under `components/three/` and must include
a static/2D fallback.

## Frontend verification

```bash
npm run lint
npm run build
```

For backend contract changes also run OpenAPI export, client generation, and the
full Python suite. For new interactive components add keyboard, reduced-motion,
offline/error, and touch-target checks.
