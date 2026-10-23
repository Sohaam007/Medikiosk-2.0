# MediKiosk 2.0 — 3D Explanation and AI Assistant Architecture

**Role:** canonical product and implementation boundary for model-aware
explanations, Blender assets, the anatomy viewer, and the patient/clinician AI
assistant.

**Status:** Product Scale Track design; not part of the frozen SEVA demo and not
clinical validation.

## Decision summary

MediKiosk does not use one general AI model to diagnose every disease or invent a
patient's anatomy. The system separates four responsibilities:

```text
disease-specific screening model
        ↓
deterministic safety and routing policy
        ↓
typed explanation contract
        ↓
3D/2D scene renderer + bounded language assistant
        ↓
clinician review
```

- **Clinical models** calculate screening outputs for a defined condition and
  input schema. They never produce a diagnosis directly.
- **Safety rules** own red flags, critical vetoes, missing-data behavior, and
  consequential action boundaries. The assistant cannot override them.
- **The explanation contract** maps model factors to approved scene IDs,
  highlight targets, patient-safe language, and fallbacks.
- **The assistant** asks questions, translates, reads content aloud, and
  explains structured results. It cannot invent anatomy, calculate risk, select
  a doctor, prescribe, book, pay, or dispatch emergency resources.
- **The 3D viewer** is progressive enhancement. Screening and intake remain
  usable without WebGL, a GPU, or a downloaded asset.

## Model and asset choices

| Responsibility | Selected approach | Boundary |
|---|---|---|
| Current cardiovascular screening | Existing local calibrated CardioVision XGBoost assets | Keep behind `CardiovascularScreeningPort`; screening only |
| Future disease screening | One model registry entry per condition/modality; calibrated baseline first, then a more complex model only when evidence supports it | No universal disease model; every version needs a model card |
| Hosted assistant | Gemini Flash-class model through the existing LLM adapter; exact model ID is configuration and must pass the project evaluation set | Language and structured explanation only; provider use is external PHI egress |
| Offline assistant | Deterministic clinical question templates, red-flag rules, and safe fallback summaries | No cloud call; no generated diagnosis |
| Clinical anatomy assets | Blender Python (`bpy`) scripts plus clinician-reviewed, licensed reference geometry | No text-to-3D output is accepted as final clinical anatomy |
| Non-clinical blockouts | Optional local Hunyuan3D-2 experiment for neutral avatars or decorative props only | Dev-only; no PHI; license and provenance review required |
| Patient-specific anatomy | Future imaging segmentation workflow, not a generative 3D model | Out of scope until imaging, consent, validation, and clinical review exist |

The current CardioVision result already supplies the correct starting data:
CAD risk, vessel-level outputs, explanation contributions, model metadata, and a
screening disclaimer. The future visualization contract must preserve those
fields and add only presentation metadata.

## What Blender produces

Blender is the authoring and deterministic build environment. The first medical
assets will be assembled from approved reference geometry and/or parametric
Blender scripts, then manually cleaned and reviewed. Blender's Python API is
appropriate for repeatable scene construction and export; the web build receives
only the reviewed GLB output.

The generation policy is:

1. Write a clinical visual brief and an allowed-claims list.
2. Select references with documented rights and provenance.
3. Build or assemble the anatomy in Blender using `bpy` scripts and manual
   review.
4. Name semantic nodes (`heart`, `lad`, `lcx`, `rca`, `lungs`, `airway`, etc.)
   so the frontend can highlight them without guessing from mesh names.
5. Create low, medium, and optional high-detail levels of detail.
6. Add only approved illustrative overlays: flow, location, inflammation-style
   education, symptom region, or risk-factor callout.
7. Export an optimized GLB and an asset manifest with checksum, license,
   triangle count, texture budget, source scene, and reviewer status.
8. Load the GLB in the frontend and verify the 2D/static fallback before the
   asset is accepted.

AI-generated geometry is not used to establish medical truth. If Hunyuan3D-2 is
used for a neutral avatar or non-clinical blockout, the output is treated as an
untrusted draft and must be rebuilt or cleaned in Blender before shipping. It is
not a runtime dependency and must not receive patient images, scans, or other
PHI.

## Disease coverage without one mesh per disease

The product uses a reusable body-system library. A disease module selects a
system, a scene, approved overlays, and a safe education script. It does not
need a unique 3D model for every condition.

| Coverage tier | What the user sees | When it is allowed |
|---|---|---|
| Tier 0 — body map | 2D symptom/body-region selection | Symptom or complaint is known, but no disease-specific scene is justified |
| Tier 1 — anatomy education | Generic organ/system anatomy | Explaining location or normal function |
| Tier 2 — screening overlay | Model-associated factors and approved highlight targets | A model returns structured, explainable screening output |
| Tier 3 — patient-specific | Segmented patient imaging or measured geometry | Future only; requires consent, imaging provenance, validation, and clinical review |

Initial reusable systems are cardiovascular, respiratory, neurological,
metabolic, renal, musculoskeletal, gastrointestinal, and skin/dermatology. The
first implementation is cardiovascular. Skin and image-heavy capabilities start
with 2D education until a validated imaging workflow exists.

## Typed explanation contract

The backend should produce a typed explanation object rather than asking the
frontend or LLM to infer a scene from prose:

```json
{
  "scene_id": "cardio.coronary-vessels",
  "mode": "illustrative-screening",
  "model_id": "cardiovision",
  "model_version": "cardiovision-assets-v1",
  "risk_band": "review",
  "explanation_factors": [
    {"feature": "HTN", "value": 1, "direction": "higher_signal"},
    {"feature": "Typical Chest Pain", "value": 1, "direction": "higher_signal"}
  ],
  "highlight_targets": ["LAD"],
  "patient_message_key": "cardio.review_required",
  "fallback_summary": "Cardiovascular screening support; clinician review required.",
  "requires_clinician_review": true,
  "disclaimer": "Illustrative screening aid; not a diagnosis or imaging result."
}
```

The `scene_id`, `highlight_targets`, and message keys must come from a local
registry. An LLM may select from the registry only after the backend has
validated the screening result; it may not create arbitrary mesh names or
clinical conclusions.

## Runtime workflow

```text
Patient voice/touch/document
        ↓
ASR/OCR/touch normalization with source and confidence
        ↓
Deterministic red-flag and consent checks
        ↓
Disease-specific screening model, if eligible
        ↓
Typed explanation contract
        ├── scene registry → GLB/2D fallback
        ├── assistant adapter → approved language/translation
        └── clinician queue → evidence and review decision
```

### Patient assistant

The patient-facing assistant is a guided workflow, not an open medical chatbot.
It may:

- ask the next approved question;
- accept a voice, touch, or button answer;
- confirm the answer in the selected language;
- explain why a screening result needs review;
- show or hide an approved scene;
- read the explanation aloud;
- provide the next safe human action.

It may not diagnose, prescribe, choose a provider, book an appointment, make a
payment, promise capacity, or downgrade a critical rule. Critical alerts are
deterministic, visible, non-dismissable until acknowledged, and recorded for
review.

### Clinician assistant

The clinician surface is an evidence co-pilot rather than a chat window. It
shows model/version metadata, input provenance, missing fields, top explanation
factors, scene status, uncertainty, and the exact disclaimer. A clinician can
ask for a structured explanation such as “why was this flagged?” and receive an
answer linked to recorded inputs, not an unsupported free-form diagnosis.

## Viewer and fallback states

The viewer must support all of these states:

| State | Required behavior |
|---|---|
| Loading | Stable placeholder, progress text, cancel/retry if applicable |
| Ready | Rotate/zoom/reset, layer legend, text equivalent, scene disclaimer |
| Partial | Show available factors and label unavailable layers |
| Error | Keep the workflow usable with the 2D/static explanation |
| Unsupported device | Use the static illustration without blocking intake |
| Offline | Use locally packaged asset and deterministic summary |
| Reduced motion | Disable pulsing/rotation and preserve the same information |
| Critical alert | Show deterministic warning above the scene; never hide it in animation |

Patient view prioritizes one clear visual, one explanation, and one next action.
Clinician view prioritizes evidence, provenance, and review controls. The same
scene must never communicate a stronger claim to the patient than the model and
clinical policy support.

## Delivery workflow and gates

Every new scene or assistant capability follows this sequence:

```text
1. Clinical intent and allowed claims
2. Data/asset/license/provenance review
3. Domain contract and model/scene registry entry
4. Deterministic mock and safe fallback
5. Blender build or asset import
6. GLB manifest/checksum/semantic-node validation
7. Backend explanation and assistant integration
8. Frontend viewer, text, keyboard, touch, and reduced-motion integration
9. Model, safety, PHI-egress, and failure-path tests
10. Browser/performance/accessibility review
11. Clinician and product-owner review
12. PR evidence, documentation update, and human merge
```

The work stops if any of these gates is missing:

- the visual claim cannot be traced to a model factor or approved education
  content;
- the source geometry or license is unknown;
- semantic node names are missing or unstable;
- the 2D/static fallback does not carry equivalent meaning;
- the assistant can bypass a deterministic veto;
- a cloud provider would receive PHI without an approved boundary;
- the frontend bundle or first interaction exceeds the agreed budget;
- a clinician reviewer has not signed off the patient-facing wording.

## Ownership

| Work | Owner | Reviewer |
|---|---|---|
| Clinical claims, safety boundaries, contracts, ADR | Soham | Pabitra + external clinical reviewer before pilot |
| Patient/clinician interaction and visual hierarchy | Soumyadeep | Soham + Pabitra |
| Screening model, explanation factors, Blender asset plan | Swapnil | Soham + Pabitra |
| Asset manifest, browser/performance/accessibility evidence | Pabitra | Soumyadeep + Soham |
| Synthetic fixtures, mock adapters, reset/offline behavior | Aditya | Pabitra + Soham |

## Evidence and implementation status

The architecture is documented, but the 3D runtime, Blender source scenes, GLB
exports, assistant contract, and multilingual assistant integration are not yet
implemented in the active runtime. The SEVA demo remains valid without them.

Implementation-specific packets must be created under `docs/tasks/active/` after
the demo freeze. The first packet should cover one CardioVision scene and its
static fallback; the assistant should be a separate packet so model, PHI, and
UI changes remain reviewable.

Related documents:

- `docs/BLENDER_PIPELINE.md` — source, export, manifest, and asset validation.
- `docs/MODEL_GOVERNANCE.md` — model lifecycle and assistant safety.
- `docs/ARCHITECTURE.md` — active runtime and future ports.
- `docs/ROADMAP.md` — Track B phase and release gates.
- `docs/decisions/0013-model-aware-explanation-and-assistant.md` — durable
  decision record for this separation.

## Technical references

- [Blender Python API](https://docs.blender.org/api/current/) — deterministic
  scene construction and export scripting.
- [Tencent Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) and its
  [community license](https://github.com/Tencent-Hunyuan/Hunyuan3D-2/blob/main/LICENSE)
  — optional non-clinical blockout reference only.
- [Gemini structured output](https://ai.google.dev/gemini-api/docs/structured-output)
  — schema-constrained assistant responses; application-level semantic
  validation is still required.
