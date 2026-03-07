---
status: accepted
date: 2026-03-07
decision-makers: project maintainer
---

# ADR-0004: TOML for Configuration, Dual-Mode CLI Output (Human / JSON)


<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Configuration Files (TOML)](#configuration-files-toml)
  - [CLI Output — Default Mode (Human-Readable)](#cli-output-default-mode-human-readable)
  - [CLI Output — JSON Mode (`--json`)](#cli-output-json-mode-json)
  - [Implementation Pattern](#implementation-pattern)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [TOML + dual-mode CLI](#toml-dual-mode-cli)
  - [YAML everywhere](#yaml-everywhere)
  - [JSON everywhere](#json-everywhere)
- [Traceability](#traceability)

<!-- /toc -->

**ID**: `cpt-cypilot-adr-toml-json-formats`

## Context and Problem Statement

Cypilot needs data formats for three distinct purposes: (1) project configuration files that humans read and edit, (2) interactive CLI output for humans working in a terminal, and (3) structured CLI output consumed by AI agents, scripts, and CI pipelines. Each purpose has different requirements — human readability, visual ergonomics, and machine parseability.

A single output format cannot serve both humans and machines well: humans need colors, progress indicators, and explanations; agents need deterministic structured data they can parse without regex.

## Decision Drivers

* **Human readability** — config files are reviewed in PRs and edited via CLI; must be readable without tooling
* **Comment support** — config files need inline documentation explaining settings
* **Interactive ergonomics** — terminal output must be scannable: colors, icons, aligned tables, progress indicators
* **Machine parseability** — AI agents, CI pipelines, and IDE plugins must consume output without parsing human-readable text
* **Channel separation** — structured data and progress messages must not intermix on the same stream
* **Stdlib availability** — Python 3.11+ includes `tomllib` for reading TOML (see `cpt-cypilot-adr-python-stdlib-only`)
* **Deterministic serialization** — config files must produce identical output for identical input (sorted keys, consistent formatting) to avoid noisy diffs

## Considered Options

1. **TOML + dual-mode CLI (human / JSON)** — TOML for config, human-readable default + `--json` for machines
2. **YAML everywhere** — YAML for both config and output
3. **JSON everywhere** — JSON for both config and output
4. **TOML config + always-JSON CLI** — TOML for config, JSON-only CLI output

## Decision Outcome

Chosen: **TOML for all configuration files; dual-mode CLI output — human-readable by default, structured JSON with `--json`**.

### Configuration Files (TOML)

All persistent configuration: `core.toml`, `artifacts.toml`, `conf.toml`, `constraints.toml`.

### CLI Output — Default Mode (Human-Readable)

Without `--json`, every command produces human-friendly output:

- **Progress messages** (headers, steps, warnings, success/error) go to **stderr** with ANSI colors and icons (`▸`, `✓`, `✗`, `⚠`)
- **Final result** is rendered by a command-specific human formatter — tables, summaries, actionable hints
- Colors auto-disable when stderr is not a TTY (piped/redirected)
- This is the mode humans interact with in the terminal

### CLI Output — JSON Mode (`--json`)

With `--json` (global flag, before the subcommand), every command outputs structured JSON:

- **Result data** goes to **stdout** as a single JSON object (`json.dumps` with `indent=2`)
- **Progress messages are suppressed** — no stderr output
- **Same data, different rendering** — the underlying result dict is identical; only the presentation layer changes
- This is the mode AI agents, CI pipelines, and IDE plugins use

Invocation pattern:
```
cpt --json <command> [options]    # → JSON to stdout
cpt <command> [options]           # → human output to stderr
```

### Implementation Pattern

All commands use a single dual-mode function (`ui.result`) that branches on the global `--json` flag:

```python
ui.result(
    data_dict,                    # always: the structured result
    human_fn=_format_for_humans,  # default mode: render to stderr
)
# --json mode: print(json.dumps(data_dict)) to stdout
```

Exit codes are consistent across modes: `0` = PASS, `1` = filesystem/config error, `2` = FAIL.

### Consequences

* Good, because TOML is human-readable and supports comments (unlike JSON)
* Good, because JSON is universally parseable by every language and tool
* Good, because `tomllib` is in Python 3.11+ stdlib — no dependency needed for reading
* Good, because clear separation: TOML = persistent config, JSON = ephemeral output
* Good, because human-readable mode provides immediate visual feedback — colors, progress, icons — without requiring any flags
* Good, because `--json` gives agents a stable, parseable contract on stdout without progress noise
* Good, because stderr/stdout separation means human progress and structured data never intermix, even if both are captured
* Bad, because TOML writing requires a custom serializer (stdlib only has reader) — mitigated by a small deterministic writer in `toml_utils.py`
* Bad, because two formats means two sets of knowledge — mitigated by clear boundary (config = TOML, output = JSON)
* Bad, because every command must provide both a data dict and a human formatter — mitigated by a generic fallback in `ui.result` and a consistent `_UI` singleton pattern

### Confirmation

Confirmed by all CLI commands supporting both human-readable (default) and `--json` modes with consistent exit codes and stderr/stdout separation.

## Pros and Cons of the Options

### TOML + dual-mode CLI

* Good, because human-readable config with comments, machine-parseable output on demand
* Good, because `tomllib` in stdlib
* Bad, because requires custom TOML writer

### YAML everywhere

* Good, because single format
* Bad, because no stdlib YAML parser in Python
* Bad, because YAML parsing gotchas (Norway problem, implicit typing)

### JSON everywhere

* Good, because universal parser support
* Bad, because no comments in config files
* Bad, because verbose and hard to read for humans

## Traceability

- **PRD**: `cpt-cypilot-nfr-simplicity` (intuitive config), `cpt-cypilot-fr-core-config`, `cpt-cypilot-fr-core-skill-engine` (machine-readable output)
- **DESIGN**: `cpt-cypilot-principle-machine-readable`, `cpt-cypilot-principle-tool-managed-config`
- **Depends on**: `cpt-cypilot-adr-python-stdlib-only` (tomllib availability)
- **Implements**: SKILL.md Agent-Safe Invocation protocol (`--json` as first argument)
