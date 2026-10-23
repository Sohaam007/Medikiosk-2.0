# MediKiosk 2.0 — Blender and 3D Asset Pipeline

Blender assets are an optional explanation and education layer. The clinical
workflow must remain usable without WebGL, GPU acceleration, or a downloaded
3D asset.

## Planned repository layout

```text
blender/
├── README.md
├── scenes/
├── scripts/
│   ├── build_heart_model.py
│   ├── build_patient_avatar.py
│   ├── export_glb.py
│   └── validate_assets.py
├── materials/
├── textures/
├── exports/
└── manifests/asset-manifest.json
```

## Asset rules

- Use synthetic anatomy and neutral avatars; never use identifiable patient
  likenesses or real clinical images without documented rights and consent.
- Keep source `.blend` files and deterministic export scripts together.
- Export web assets as optimized GLB/GLTF with a manifest containing checksum,
  dimensions, triangle count, texture sizes, and license.
- Keep the initial page usable before the asset loads.
- Provide a static SVG/image/text explanation for low-power and reduced-motion
  users.
- Do not encode clinical conclusions into animation that the model does not
  support; visuals must map to explicitly named explainability factors.

## Frontend contract

The future viewer should receive a typed payload containing:

```text
model_id
model_version
risk_band
explanation_factors[]
highlight_targets[]
disclaimer
fallback_summary
```

It must support loading, error, unsupported-device, reduced-motion, and offline
states. 3D is progressive enhancement, not a dependency of screening.

## Validation gate

Before accepting an asset:

1. run the export from a clean Blender environment;
2. validate the manifest and checksum;
3. inspect GLB loading in the frontend build;
4. measure bundle and first-interaction impact;
5. verify keyboard/text fallback and reduced motion;
6. record licenses and the source scene.

## Generation decision

The default generator for clinical anatomy is **Blender itself**, driven by
deterministic Blender Python (`bpy`) scripts and clinician-reviewed, licensed
reference geometry. A text-to-3D model is not accepted as the final source of
medical anatomy.

Optional AI-generated geometry may be used only for neutral avatars or
non-clinical blockouts. The current experimental candidate is local Hunyuan3D-2,
but it is not a runtime dependency, must not receive patient data, and requires
license/provenance review before any output is kept. Every such draft must be
rebuilt or manually cleaned in Blender and assigned stable semantic node names.

Hunyuan3D-2 is not a default product dependency because its community license
has territory, distribution, notice, and acceptable-use conditions. In
particular, the published license excludes the European Union, United Kingdom,
and South Korea. A future team may use it only after checking the deployment
territory and recording the required notice and license decision.

Patient-specific anatomy is a separate future workflow based on consented
medical-image segmentation. It is not generated from a CardioVision risk score
and is not part of the current 3D feature.

## Required asset workflow

```text
clinical brief and allowed claims
→ reference/license manifest
→ Blender scene assembly or deterministic script
→ topology/material/semantic-node cleanup
→ low/medium detail variants
→ GLB export
→ manifest/checksum/license validation
→ frontend viewer + equivalent 2D fallback
→ performance/accessibility/reduced-motion checks
→ clinician wording and safety review
→ PR evidence and human approval
```

The first Track B asset is one CardioVision heart/coronary scene. It may
highlight approved vessel targets and risk factors, but it must not display a
patient-specific blockage, diagnosis, or treatment recommendation.

See `docs/3D_AND_ASSISTANT_ARCHITECTURE.md` and ADR 0013 for the complete
model/assistant separation and promotion gates.

Reference sources: Blender Python API documentation and the official Tencent
Hunyuan3D-2 repository/license. These are implementation references, not
clinical validation evidence.
