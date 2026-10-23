# MediKiosk 2.0 — Model Governance

This guide applies to CardioVision and every future cognitive, metabolic,
respiratory, or multi-disease model.

## Model lifecycle

```text
problem definition
→ data provenance and consent review
→ baseline model
→ offline evaluation
→ calibration and subgroup analysis
→ safety threshold review
→ model card and manifest
→ deterministic integration tests
→ sandbox shadow mode
→ monitored promotion
→ rollback or retirement
```

## Required model artifacts

Every model version must have:

- `model_id` and semantic `model_version`;
- input schema and unit/range definitions;
- preprocessing and missing-data policy;
- training/evaluation data provenance;
- ROC-AUC and PR-AUC where applicable;
- calibration curve, Brier score, and expected calibration error;
- sensitivity, specificity, PPV, NPV, and threshold rationale;
- subgroup results relevant to deployment;
- out-of-distribution and invalid-input behavior;
- explainability method and known limitations;
- clinician-review and emergency-veto policy;
- latency/resource profile;
- license and artifact checksum;
- rollback version.

Recommended location:

```text
models/<model-id>/
├── manifest.json
├── model-card.md
├── calibration.json
├── evaluation.json
└── artifact files
```

## Product safety rules

- Model probability is not diagnosis.
- A model cannot override deterministic emergency/veto rules.
- Model output cannot directly trigger payment, booking, medication changes,
  emergency dispatch, or patient messaging without an approved service policy.
- Missing or invalid inputs produce an explicit “insufficient data” state.
- Every UI result displays model/version and clinician-review language.
- Model failures fail closed to safe manual review or offline continuation.

## Evaluation commands

The evaluation harness is expected to live under `eval/` and must be runnable
offline against synthetic or approved de-identified data. A report must include
the command, dataset manifest, random seed, environment, and output checksum.

Do not use a single aggregate AUC as the sole release criterion. The `>90% AUC`
product target is a hypothesis requiring measured evidence, not a default claim.

## Model roles in the product

MediKiosk distinguishes three different kinds of AI capability:

| Capability | Allowed responsibility | Not allowed |
|---|---|---|
| Screening model | Produce a versioned, calibrated screening estimate from its declared inputs | Diagnose, prescribe, or bypass a deterministic veto |
| LLM assistant | Ask approved intake questions, translate, summarize, read aloud, and explain validated structured output | Calculate clinical risk, invent evidence, select arbitrary anatomy, book, pay, or dispatch |
| 3D asset workflow | Render approved anatomy education and model-associated explanation overlays | Establish medical truth, show an inferred patient lesion, or turn a risk score into a diagnosis |

The current hosted assistant candidate is a configurable Gemini Flash-class model
behind the existing provider adapter. The exact provider/model ID must remain
configuration and must pass the repository's structured-output, multilingual,
timeout, PHI-egress, and offline-fallback tests. The offline assistant is the
deterministic clinical fallback engine and approved templates, not an untested
local LLM.

## Explanation and provenance requirements

Every model-aware visual or assistant answer must carry:

- `model_id` and `model_version`;
- input facts and their source (`patient`, `informant`, `document`, `device`, or
  `model`);
- missing/invalid input state;
- approved `scene_id` or an explicit static fallback;
- explanation factors and highlight targets;
- screening-only or educational mode;
- clinician-review requirement;
- exact disclaimer and next safe action.

The LLM may fill language fields only after backend validation. It may choose
from an allowlisted scene registry but may not create mesh targets, clinical
labels, thresholds, or actions. Critical alerts remain deterministic and
non-dismissable until acknowledged.

## Asset governance

Clinical Blender assets follow the same evidence discipline as model artifacts:

- source geometry and license are recorded;
- build scripts and Blender version are pinned;
- semantic anatomy node names are stable;
- GLB checksum and optimization metrics are recorded;
- a text/2D equivalent exists;
- clinician wording review is recorded;
- no PHI or patient images enter a generative asset service.

The detailed asset workflow is canonical in
`docs/3D_AND_ASSISTANT_ARCHITECTURE.md` and `docs/BLENDER_PIPELINE.md`.
