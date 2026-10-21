# Unverified and Environment-Dependent Items

This is the current verification gap list. A local mock or passing unit test
does not remove an item that requires an external environment or physical asset.

| Area | Current gap | Evidence required before promotion |
|---|---|---|
| ABDM/ABHA | Local QR/webhook/SSE simulation only | Approved sandbox callback, signature/auth proof, consent/readback, rollback. |
| PM-JAY | Mock eligibility adapter | NHA sandbox/production verification with approved credentials. |
| WhatsApp | Mock notification adapter | Meta sandbox delivery and receipt evidence with opt-in/opt-out. |
| LLM | Gemini/OpenAI provider calls not locally verified with governed PHI policy | Staging provider test, egress review, retention agreement, redacted logs. |
| ASR | Deterministic mock transcription route | Language-specific medical-speech benchmark and provider failure tests. |
| OCR | Provider-capable LLM path, no representative benchmark recorded | Synthetic/de-identified corpus metrics and human review. |
| CardioVision | Local model assets, no complete clinical evaluation report | Model card, calibration, subgroup, threshold, and external validation evidence. |
| FHIR | Local minimal/FHIR-shaped output | External validator pass and destination acceptance. |
| Hospital routing | Local catalog/referral candidates | Fresh authenticated partner data, availability timestamp, human confirmation. |
| Payments | UI/domain groundwork | Provider webhook, reconciliation, refund, and emergency bypass tests. |
| Travel/tourism | Product target only | Partner contracts, pricing freshness, visa/travel policy, and safe booking flow. |
| Hardware | Browser simulation only | Touchscreen, webcam, microphone, printer, kiosk lockdown, and power-loss tests. |
| Blender/3D | No active asset pipeline | Clean export, manifest, performance, accessibility, and fallback evidence. |
| Production ops | Local Docker/launcher only | Managed secrets, migrations, monitoring, backup/restore, security scans, rollback drill. |
