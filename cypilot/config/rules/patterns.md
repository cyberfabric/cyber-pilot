---
cypilot: true
type: project-rule
topic: patterns
generated-by: auto-config
version: 1.0
---

# Patterns


<!-- toc -->

- [Error Handling](#error-handling)
  - [Error Propagation via Tuples](#error-propagation-via-tuples)
  - [Return Tuples in Proxy](#return-tuples-in-proxy)
  - [JSON Output Contract](#json-output-contract)
  - [Exit Codes](#exit-codes)
- [Performance](#performance)
  - [Lazy Imports](#lazy-imports)
- [Integrity](#integrity)
  - [AGENTS.md Auto-Repair](#agentsmd-auto-repair)
- [Testing](#testing)
  - [Test Bootstrap Pattern](#test-bootstrap-pattern)

<!-- /toc -->

Recurring implementation patterns and idioms observed in the Cypilot codebase.

## Error Handling

### Error Propagation via Tuples

Utility functions return `(result, error_list)` tuples rather than raising. The caller decides whether to abort or collect. Validation commands aggregate all issues into a JSON report.

Evidence: `utils/context.py:57-58` (`load_artifacts_meta` returns `(meta, err)`), `utils/constraints.py` (`load_constraints_toml` returns `(constraints, errors)`).

### Return Tuples in Proxy

Proxy functions return `Tuple[bool, str]` (success flag + message) or `Tuple[Optional[Path], str]` (path + source). Never raise exceptions across package boundaries — return error info in the tuple.

Evidence: `cache.py:66-68` (`download_and_cache`), `resolve.py:189-210` (`resolve_skill`).

### JSON Output Contract

All CLI commands print machine-readable JSON to stdout. Use `json.dumps(..., indent=None, ensure_ascii=False)` for single-line output, `indent=2` for verbose/report output. Always include a `"status"` field (`"PASS"`, `"FAIL"`, or `"ERROR"`). Write human messages to stderr.

Evidence: `commands/validate.py:39-40`, `cli.py:174-179`.

### Exit Codes

- `0` — success / PASS
- `1` — error (bad args, missing config, tool failure)
- `2` — validation FAIL (deterministic validation found issues)

Evidence: `commands/validate.py:70`, `cli.py` return values.

## Performance

### Lazy Imports

Skill CLI uses deferred imports inside command thunks to keep startup fast. Import heavy modules (commands, context) only when the specific command is dispatched.

Evidence: `cli.py:18-111` (all `_cmd_*` functions use local imports).

## Integrity

### AGENTS.md Auto-Repair

Every CLI invocation (except `init`) silently verifies and re-injects the root `AGENTS.md` managed block. This ensures the navigation hub stays in sync even if a user edits the file.

Evidence: `cli.py:192-206`.

## Testing

### Test Bootstrap Pattern

Tests create isolated project trees in `TemporaryDirectory`, using helpers like `_bootstrap_project_root()` or `_bootstrap_registry()` to set up minimal config. Always `os.chdir()` into the temp dir with a `try/finally` to restore cwd.

Evidence: `tests/test_validate.py:32-47`, `tests/conftest.py:7-14`.
