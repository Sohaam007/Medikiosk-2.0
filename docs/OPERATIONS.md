# MediKiosk 2.0 — Operations and Deployment

The project currently supports local development and a backend container. A
production deployment requires additional operational evidence; this document
keeps those requirements visible.

## Local modes

### Windows development

Use `start_dev.bat` to start the API and Vite frontend. It is a developer
launcher, not a production supervisor.

### Backend container

```bash
```

The root container runs the FastAPI backend only. The Vite frontend is built and
served separately unless a future deployment image explicitly combines them.

### Compose

`docker-compose.yml` describes PostgreSQL, Redis, and API development services,
but the active dependency container currently uses in-memory cache. Verify the
compose environment and adapter wiring before calling Redis production-ready.

## Production prerequisites

- pinned and reproducible image build;
- managed secrets and rotation;
- approved CORS/TLS/mTLS configuration;
- PostgreSQL migrations and backup/restore;
- real cache adapter if required;
- structured logs, metrics, traces, and redaction;
- rate limiting and gateway request limits;
- provider health/readiness and circuit breakers;
- PHI retention/purge and access audit;
- vulnerability, secret, SBOM, and container scans;
- clinical governance and incident ownership;
- tested rollback and disaster recovery.

## Health model

Separate:

- liveness: process can respond;
- readiness: database/cache/providers required for the selected mode are usable;
- integration health: provider credentials and signed test/readback are valid;
- clinical safety health: model/version/threshold configuration is approved.

Do not report an external integration as healthy merely because the API process is
alive.

## Incident priorities

1. Patient-safety or emergency-routing failure.
2. PHI exposure or unauthorized provider egress.
3. Incorrect model/version/threshold behavior.
4. Data loss, purge failure, or audit-chain failure.
5. Provider delivery or queue failure.
6. UI/deployment availability issue.

Each incident requires containment, evidence preservation without copying PHI,
credential rotation where needed, rollback/feature disablement, and a sanitized
post-incident record.
