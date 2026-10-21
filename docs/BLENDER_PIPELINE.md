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
