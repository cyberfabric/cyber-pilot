# Phase 2 Critical Runtime Errors

## Enabled pylint IDs

- `E0602`
- `E1135`
- `E0102`

## Scope confirmation

- Enabled only the Phase 2 message IDs in `pyproject.toml`
- Preserved the disable-all staged rollout baseline
- Did not enable any `W*`, `R*`, or `C*` diagnostics

## Files changed

- `pyproject.toml`
- `skills/cypilot/scripts/cypilot/utils/manifest.py`
- `skills/cypilot/scripts/cypilot/utils/coverage.py`
- `skills/cypilot/scripts/cypilot/utils/artifacts_meta.py`
- `skills/cypilot/scripts/cypilot/commands/agents.py`
- `tests/test_subagent_registration.py`

## Fix summary

- Added missing `Tuple` import used by `resolve_resource_bindings_with_errors()` annotations
- Added missing `Any` import used by coverage helper annotations
- Removed the duplicate `ArtifactsMeta.get_kit()` definition that triggered `E0102`
- Normalized registered-kit filtering in `agents.py` to concrete `set[str]` values before membership checks
- Added a regression test proving `_discover_kit_agents()` ignores invalid registered-kit helper output instead of failing

## Verification

### Lint

Command:

```text
make pylint
```

Result:

```text
Running pylint...
```

Outcome: PASS

### Targeted tests

Command:

```text
PYTHONPATH=src:skills/cypilot/scripts pytest -q -p no:cacheprovider tests/test_manifest.py tests/test_coverage_utils.py tests/test_subagent_registration.py
```

Result:

```text
106 passed in 0.58s
```

Outcome: PASS

## Residual backlog intentionally deferred

- Phase 3 warning-family diagnostics remain disabled and were not addressed in this phase
- Any refactor, convention, duplication, import-format, naming, or docstring cleanup remains deferred to later phases by plan design
