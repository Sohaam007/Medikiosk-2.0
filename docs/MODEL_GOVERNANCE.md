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
