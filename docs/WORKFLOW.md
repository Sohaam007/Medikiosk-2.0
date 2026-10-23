# MediKiosk 2.0 — Engineering Workflow

This is the working agreement for humans and coding agents. The executable
commands in `docs/TESTS.md` and project configuration are authoritative.

## Branches

Use one branch per bounded capability:

```text
feat/<scope>-<slug>
fix/<scope>-<slug>
refactor/<scope>-<slug>
docs/<scope>-<slug>
chore/<scope>-<slug>
```

Keep the branch focused. Do not mix a feature, broad refactor, dependency
upgrade, and provider migration unless the task packet explicitly combines them.

## Pull-request-only rule

`main` is a protected integration branch. Agents and contributors must not
commit or push directly to it. Work starts from an up-to-date `main` checkout on
one of the task branch forms above, then proceeds through a pull request.

The allowed agent boundary is:

```text
create branch → commit task-scoped changes → push task branch → open/update PR
→ collect required review and checks → human owner merges
```

Agents must not merge a PR. GitHub branch protection rejects direct pushes and
force pushes for normal contributors. The repository owner/admin account
`@Sohaam007` is the intentional exception and may bypass the review gate when
the owner chooses to do so; this does not grant bypass rights to other members.
Local instructions remain a required contributor workflow, not a substitute for
the remote rule.

Before pushing, the author must inspect:

```bash
git status --short --branch
```

Only files allowed by the task packet may be staged.

## Commit format

```text
<type>(<scope>): <imperative description>
```

Allowed types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`.

Examples:

```text
feat(screening): add cognitive screening contract
fix(auth): reject expired development tokens
docs(agents): clarify mock integration boundaries
```

## Required feature order

```text
research current code
→ write acceptance criteria
→ ADR if needed
→ contract
→ port
→ mock adapter
→ domain/service logic
→ API route
→ OpenAPI export
→ generated client
→ frontend feature
→ focused tests
→ regression map checks
→ full checks
→ docs/status update
→ commit
```

Do not make the frontend invent an API shape before the backend contract is
settled. Do not connect a provider before a mock and failure policy exist.

## ADR triggers

Create a new sequential ADR in `docs/decisions/` before merging when a change:

- adds or widens a required domain contract field;
- adds a dependency, provider, model, database, or deployment technology;
- changes authentication, consent, PHI retention, or external egress;
- changes dependency direction or reactivates a legacy tree;
- changes clinical thresholds, veto behavior, or commercial-flow safety;
- introduces a new persistence or migration strategy;
- changes the generated API contract in a breaking way.

## Review checklist

Reviewers must verify:

- requested behavior and acceptance criteria;
- active path and allowed file scope;
- contract/port compatibility;
- auth, consent, and external egress;
- PHI logging and fixture safety;
- critical-veto/commercial-flow behavior;
- deterministic/offline fallback;
- generated OpenAPI and client sync;
- focused and downstream tests;
- docs/status/ADR updates;
- rollback and migration safety.

## Pull request evidence

Every PR should state:

1. user-visible result;
2. feature ID and task packet;
3. human owner and reviewer(s);
4. files changed and why;
5. exact checks run;
6. external services/modes used;
7. generated artifacts;
8. unverified claims or remaining risks;
9. rollback path;
10. confirmation that no unrelated files are included.

## Release sequence

```text
local focused checks
→ full backend/frontend checks
→ security and generated-artifact review
→ clean-clone/container verification
→ staging/sandbox verification
→ human approval
→ release
→ post-release health/readback
```

No local mock result is a release-readiness proof for a provider integration.
