# ADR 0013: Separate Clinical Models, 3D Explanations, and the AI Assistant

> **Status:** Proposed
> **Date:** 2026-10-23
> **Author:** Project team (drafted for review)
> **Reviewers:** Soham, Soumyadeep, Swapnil, Pabitra, Aditya

## Context

The product roadmap includes multi-disease screening, Blender/GLB education
assets, and a multilingual assistant. These capabilities could become unsafe or
unreproducible if a general-purpose LLM is allowed to diagnose, invent anatomy,
select arbitrary 3D assets, or trigger consequential actions.

The current repository already has a bounded CardioVision screening adapter,
model explanations, a 2D body map, a placeholder assistant avatar, Gemini and
OpenAI provider seams, and an offline fallback path. It does not yet have a
3D runtime, a scene registry, or a typed assistant/explanation contract.

## Decision

MediKiosk will use four separate layers:

1. **Disease-specific screening models** produce calibrated, explainable
   screening outputs for a declared input schema. CardioVision remains the first
   local XGBoost implementation.
2. **Deterministic clinical and safety policy** owns red flags, critical vetoes,
   missing-data behavior, consent, routing boundaries, and human-review gates.
3. **A typed explanation contract and local scene registry** map validated model
   factors to approved scene IDs, semantic highlight targets, safe message keys,
   and 2D/static fallbacks.
4. **A bounded AI assistant** handles question phrasing, translation, read-out,
   and explanation of structured outputs. It cannot calculate risk, diagnose,
   prescribe, book, pay, select a provider, or override a safety policy.

### Blender asset generation

Clinical anatomy will be created or assembled in Blender using deterministic
Blender Python (`bpy`) scripts and clinician-reviewed, licensed reference
geometry. The final artifact is a reviewed GLB with semantic node names and a
manifest. A text-to-3D generator is not an authority for medical anatomy.

Hunyuan3D-2 may be evaluated locally for neutral avatars or decorative,
non-clinical blockouts. It is not a runtime dependency, must not receive PHI,
and cannot be promoted to a shipped clinical asset without provenance, license,
topology, visual, and clinical review. Patient-specific anatomy is reserved for
a future consented medical-imaging segmentation workflow.

### Assistant provider

The first hosted assistant remains behind the existing LLM provider adapter and
uses a configurable Gemini Flash-class model after the project evaluation set
passes. The exact model ID is configuration, not domain logic. The offline path
uses deterministic question templates, safety rules, and fallback summaries.

## Alternatives considered

### One multimodal LLM for diagnosis, 3D, and conversation

Rejected. It would mix probabilistic language generation with clinical policy,
make evidence tracing difficult, and allow unsupported visual or diagnostic
claims.

### Text-to-3D generation for final anatomy

Rejected. Generated geometry may be visually plausible but clinically wrong,
unstable across runs, difficult to license, and difficult to map to reliable
semantic anatomy targets.

### Cloud-only assistant and asset generation

Rejected as the default. It creates external PHI and availability boundaries,
breaks offline operation, and makes reproducible builds harder. Cloud use may be
enabled only through an approved adapter and explicit data/consent review.

### No visual explanation layer

Rejected for the product-scale experience. A visual layer can improve patient
understanding, but it must remain optional and must never block intake or
clinician review.

## Consequences

### Positive

- Clinical decisions remain separate from language generation and rendering.
- The same anatomy scene can support multiple approved disease modules.
- Offline and low-power fallbacks remain first-class behavior.
- Model, asset, license, and assistant evidence can be reviewed independently.
- The SEVA demo remains stable while Track B is developed.

### Negative

- The team must maintain scene manifests, model registries, and typed contracts.
- Blender source files and exports require asset QA in addition to frontend QA.
- Some disease concepts will use 2D education until a safe 3D scene exists.
- A hosted assistant needs explicit PHI-egress, cost, timeout, and failure
  controls.

## Rollback and promotion

- Keep the 3D feature behind a capability flag and retain the static explanation.
- Revert to the previous model registry entry if evaluation or runtime checks
  fail.
- Disable the hosted assistant and use deterministic fallback when credentials,
  consent, quota, or validation are unavailable.
- Do not promote a scene or model from synthetic demo to patient use without the
  clinical/regulatory readiness gate in ADR 0012.

## Required follow-up

- Add the typed explanation contract and scene registry through a bounded task
  packet.
- Pin the Blender runtime and record the exact export command.
- Create one CardioVision heart scene and a semantically equivalent 2D fallback.
- Add assistant schema, allowlisted actions, PHI-egress tests, and offline tests.
- Obtain team review of this ADR before implementing the Track B capability.
