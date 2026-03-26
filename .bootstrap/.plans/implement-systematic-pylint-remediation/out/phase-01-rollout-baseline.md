# Phase 1 Rollout Baseline

## Scope

This phase established the repository-wide pylint rollout mechanism only. It did not perform broad source cleanup.

## Authoritative pylint baseline

- Authoritative config file: `pyproject.toml`
- Canonical messages-control baseline:
  - `[tool.pylint."messages control"]`
  - `disable = ["all"]`
- Preserved non-message settings:
  - `[tool.pylint.main]` jobs, persistence, Python version, ignore paths
  - `[tool.pylint.format]` max line length
  - `[tool.pylint.design]` argument thresholds
  - `[tool.pylint.reports]` score setting

## Local and CI contract

- Canonical local entrypoint remains: `make pylint`
- Canonical CI entrypoint remains: `.github/workflows/ci.yml` → `make pylint`
- Lint targets remain unchanged:
  - `src/cypilot_proxy`
  - `skills/cypilot/scripts/cypilot`

## Makefile rollout support

`Makefile` keeps the same `pylint` target and the same target set. The only rollout-specific behavior added is:

- If pylint exits with code `32` because all messages are disabled and it reports `No files to lint`, `make pylint` treats that exact condition as a clean baseline and exits successfully.
- Any other pylint exit code still fails the target.

This preserves the existing `make pylint` contract while allowing a true disable-all starting point for staged re-enable.

## Verification run

Executed command:

```text
make pylint
```

Observed result:

```text
Running pylint...
No files to lint: exiting.
Pylint baseline has all messages disabled; treating 'No files to lint' as a clean rollout baseline.
```

Verification outcome:

- Baseline command status: PASS
- Baseline cleanliness: clean under disable-all baseline
- Enabled-diagnostic failure behavior: unchanged for any later phase, because non-32 pylint failures still propagate

## TDD and scope note

No Python source behavior was changed in this phase. The only executable change was the lint-entrypoint shell behavior needed to preserve `make pylint` under a disable-all baseline. The required validation for this phase was the mandated `make pylint` execution itself.
