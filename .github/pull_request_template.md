## Feature or task

- Feature ID:
- Human owner:
- Reviewer(s):
- Task packet:
- Branch:

## User-visible result

<!-- What becomes possible, safer, clearer, or more reproducible? -->

## Scope control

- Allowed paths:
- Forbidden paths:
- Explicitly out of scope:

## Verification evidence

List the exact commands that were actually run and their results.

- [ ] Focused check:
- [ ] Downstream regression checks:
- [ ] Full backend checks, when applicable:
- [ ] Frontend lint/build, when applicable:
- [ ] Browser/accessibility/manual check, when applicable:
- [ ] Documentation or repository-hygiene check:

## Contract, safety, and data review

- [ ] No direct push to `main`; this work is on a task branch.
- [ ] No secrets, PHI, raw patient files, or private captures were added.
- [ ] Mock/offline behavior is distinct from sandbox or live behavior.
- [ ] Auth, consent, PHI egress, timeout, retry, and idempotency behavior were reviewed.
- [ ] Critical-patient commercial-flow veto behavior is preserved.
- [ ] An ADR was added if a contract, dependency, provider, model, security boundary,
      persistence strategy, clinical threshold, or legacy-tree boundary changed.

## Generated and documentation changes

- [ ] OpenAPI and generated client were regenerated together, if the API changed.
- [ ] `docs/FEATURES.md` status/PR link is updated.
- [ ] Canonical documentation owner was updated, if a fact changed.
- [ ] No unrelated or unnecessary files are included.

## Rollback

<!-- How can this change be disabled, reverted, or safely rolled back? -->

## Remaining risks or unverified claims

<!-- Be explicit about anything not tested, not live, or not clinically validated. -->
