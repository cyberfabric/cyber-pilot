---
cypilot: true
type: project-rule
topic: anti-patterns
generated-by: auto-config
version: 1.0
---

# Anti-Patterns


<!-- toc -->

- [Import Across Packages](#import-across-packages)
- [Shared Mutable State](#shared-mutable-state)
- [Raising in Utilities](#raising-in-utilities)
- [Hardcoded Layout Paths](#hardcoded-layout-paths)
- [Non-JSON Stdout](#non-json-stdout)
- [Blocking Imports in cli.py](#blocking-imports-in-clipy)

<!-- /toc -->

Project-specific things NOT to do, based on patterns observed in the Cypilot codebase.

## Import Across Packages

**Don't**: Import from `cypilot_proxy` inside the skill engine or vice versa.
**Why**: They are separate packages communicating only via subprocess.
**Do**: Use `subprocess.run` for cross-package calls.

## Shared Mutable State

**Don't**: Add module-level mutable state beyond `_context`.
**Why**: Complicates testing and makes behavior unpredictable.
**Do**: Pass state via function parameters.

## Raising in Utilities

**Don't**: Raise exceptions from utility functions.
**Why**: Callers need to aggregate errors into JSON reports.
**Do**: Return `(result, errors)` tuples. Only raise in tests or at the CLI boundary.

## Hardcoded Layout Paths

**Don't**: Hardcode `cypilot/.core/` or `cypilot/.gen/` as string literals.
**Why**: Layout may change; helpers exist for this purpose.
**Do**: Use `core_subpath()` / `gen_subpath()` from `utils/files.py`.

## Non-JSON Stdout

**Don't**: Print human-readable text to stdout from CLI commands.
**Why**: Downstream tools parse stdout as JSON.
**Do**: Use `json.dumps(...)` for stdout. Write human messages to stderr.

## Blocking Imports in cli.py

**Don't**: Import command modules at the top of `cli.py`.
**Why**: Slows startup for every invocation, even `--version`.
**Do**: Use lazy imports inside command thunk functions (`_cmd_{name}`).
