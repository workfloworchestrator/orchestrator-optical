# Patch-coverage gate is a temporary 50% floor

- **Status:** open
- **Severity:** low
- **Area:** ci
- **Affected:** `.github/workflows/ci.yml:71-74` (integration job, `diff-cover coverage.xml --compare-branch=origin/main --fail-under=50`).
- **Discovered by:** CI integration job / `diff-cover` report on this branch.

## Symptom

The patch-coverage gate on PRs is set to 50%, which is low enough that substantial new
uncovered code can pass review. The threshold was chosen only because measured patch
coverage on this in-progress branch is ~56-67%; the inline comment already flags it as
temporary.

## Root cause

The branch is mid-port and patch coverage has not yet stabilised, so a stricter gate would
fail constantly. 50% was picked to leave headroom rather than to reflect a quality target.

## Proposed fix

- Raise `--fail-under` in `.github/workflows/ci.yml` as patch coverage improves, in steps
  (e.g. 60 → 70 → 80).
- Document the target (e.g. 80%) in the job comment so the intent is explicit and the
  ratchet direction is unambiguous.

## Acceptance criteria

- CI passes at the raised threshold on the integration job.
- The threshold and the documented target agree, and the comment no longer describes 50%
  as the intended floor.

## References

- `.github/workflows/ci.yml:71-74`.
- Current status notes: `todo/testing-architecture.md:44` (finding #5).
- Coverage ratchet: `coverage-floors.toml`, `scripts/coverage_ratchet.py`.
