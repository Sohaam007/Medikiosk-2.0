# MediKiosk 2.0 — Security and Privacy Baseline

This document distinguishes controls visible in the current repository from
controls required before production. A planned control is not an implemented
control.

## Data classification

| Data | Classification | Rules |
|---|---|---|
| Session UUID, event type, timing metadata | Operational | May be logged if not linkable to patient identity. |
| Name, phone, ABHA, Aadhaar, address | Direct identifier/PHI | Do not log; encrypt/protect at rest and in transit. |
| Symptoms, diagnoses, medicines, labs, transcripts, OCR, audio | Clinical PHI | Minimize, consent, restrict access, purge on policy. |
| Model probabilities/explanations | Sensitive clinical inference | Show review boundary; do not call diagnosis. |
| API keys, JWT secrets, provider payloads | Secret/security-sensitive | Environment/secret manager only; never commit or log. |

## Controls currently visible

- `.env` and local databases/uploads are ignored by Git.
- Settings uses `SecretStr` for sensitive configuration fields.
- Core routes use role-based JWT dependencies.
- Upload routes validate allowlisted MIME types, size, and empty input.
- Domain error and validation handlers avoid returning raw stack traces.
- Audit contracts and invariant tests exist.
- LLM adapters include anti-injection preambles and structured-output parsing.
- CardioVision output is bounded by a screening-only policy.
- Session purge and walk-away privacy flows exist in the application model.

## Controls requiring verification or implementation

- A complete route-level auth/signature matrix, especially ABDM webhook/SSE.
- TLS/mTLS, certificate handling, provider request signing, and egress controls.
- Managed secret store and production secret rotation.
- Application-level encryption/key management for persisted PHI.
- Rate limiting and request/header limits at the actual gateway.
- Real FHIR validation and destination authorization.
- External provider data-retention agreements and consent enforcement.
- Docker build-context exclusion via `.dockerignore`.
- Dependency, secret, container, SBOM, and vulnerability scans in CI.
- Kiosk TPM/secure boot/USB lockdown and physical hardware validation.
- Backup, restore, deletion, breach, and incident-response drills.

## AI/LLM threat rules

- Treat all patient speech, OCR, documents, and external provider responses as
  untrusted input.
- Use parameterized prompts and schema validation.
- Do not carry conversation history between patients or sessions.
- Bound text, image, audio, token, and response sizes.
- Reject or quarantine malformed model output.
- Do not allow model output to execute tools or consequential actions directly.
- Require clinician review for screening, routing, medication, and emergency
  recommendations.

## Integration security checklist

Before sandbox/production promotion, verify:

```text
credential source and rotation
→ request authentication/signature
→ consent and role checks
→ timeout/retry/idempotency
→ webhook replay protection
→ PHI minimization and redaction
→ audit event without raw payload
→ provider failure and rollback
→ delivery/readback evidence
```

## Reporting rule

Security documentation must label each statement as one of:

- `implemented` — backed by current code/tests;
- `configured` — exists but depends on deployment settings;
- `verified` — dated evidence exists;
- `planned` — target work only;
- `unverified` — expected but not proven.
