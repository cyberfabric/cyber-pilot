---
status: accepted
date: 2026-03-13
decision-makers: project maintainer
---

# ADR-0015: Prefer `cpt` CLI over Direct Script Invocation for AI Agents

**ID**: `cpt-cypilot-adr-prefer-cpt-cli-for-agents`

<!-- toc -->

- [Context and Problem Statement](#context-and-problem-statement)
- [Decision Drivers](#decision-drivers)
- [Considered Options](#considered-options)
- [Decision Outcome](#decision-outcome)
  - [Consequences](#consequences)
  - [Confirmation](#confirmation)
- [Pros and Cons of the Options](#pros-and-cons-of-the-options)
  - [Option 1: Prefer cpt with Graceful Fallback](#option-1-prefer-cpt-with-graceful-fallback)
  - [Option 2: Always Use Direct Script Path](#option-2-always-use-direct-script-path)
  - [Option 3: Require cpt with No Fallback](#option-3-require-cpt-with-no-fallback)
- [More Information](#more-information)
- [Traceability](#traceability)

<!-- /toc -->

## Context and Problem Statement

Cypilot's SKILL.md instructs AI agents (Claude, Cursor, Copilot, etc.) to invoke the skill engine via a raw Python path: `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json <command>`. This works but creates several problems: the invocation is fragile (depends on the correct `python3` being on PATH with `tomllib` support — Python 3.11+), the command is long and error-prone for LLMs to reproduce, and it looks nothing like a standard Unix tool. Meanwhile, a global `cpt` CLI proxy already exists (ADR-0003, ADR-0007) that handles interpreter resolution, version negotiation, and command forwarding — but SKILL.md never references it.

## Decision Drivers

* **LLM ergonomics** — AI agents handle short, conventional CLI commands (`cpt validate`) far more reliably than long interpreter-qualified paths; fewer tokens, fewer transcription errors
* **Interpreter independence** — `cpt` is installed via `pipx` which pins its own Python interpreter; the agent never needs to guess whether `python3` is 3.9 or 3.13
* **Unix convention** — a single-word command on PATH is the standard interface for CLI tools; agents are trained on this pattern and reproduce it more accurately
* **Zero-regression fallback** — environments where `cpt` is not installed must continue to work via the direct script path
* **Minimal friction** — the agent should detect availability automatically and not block the user if `cpt` is absent

## Considered Options

1. **Prefer `cpt` with graceful fallback** — detect `cpt` on PATH at session start; use it if available; fall back to direct script path if not; prompt user once per session about installation
2. **Always use direct script path** — keep the current approach; ignore `cpt` in agent prompts entirely
3. **Require `cpt` with no fallback** — mandate `cpt` installation; refuse to proceed without it

## Decision Outcome

Chosen option: **Option 1 — Prefer `cpt` with graceful fallback**, because it gives agents the ergonomic benefits of a standard CLI command while maintaining backward compatibility for environments where `cpt` is not yet installed. The detection is a single `command -v cpt` check at session start with no ongoing cost.

### Consequences

* Good, because agent invocations become shorter and more reliable (`cpt --json validate` vs. `python3 /long/path/cypilot.py --json validate`)
* Good, because interpreter version mismatches are eliminated when `cpt` is available — `pipx` manages the Python version
* Good, because the pattern matches what LLMs are trained on — standard Unix CLI tools
* Good, because the fallback path preserves full functionality for environments without `cpt`
* Neutral, because users without `cpt` see a one-time installation prompt with persistent dismissal — once dismissed, the prompt does not reappear (state stored in `~/.cypilot/cache/cpt-prompt-dismissed`)
* Bad, because adds a detection step at session start (negligible cost — single `command -v` call)

### Confirmation

Confirmed when:

- SKILL.md references `{cpt_cmd}` instead of the hardcoded Python script path
- An agent session with `cpt` installed uses `cpt --json <command>` for all invocations
- An agent session without `cpt` falls back to `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py` and functions identically
- The user is prompted about `cpt` installation when it is not found, with persistent dismissal — dismissed users are not prompted again

## Pros and Cons of the Options

### Option 1: Prefer cpt with Graceful Fallback

Detect `cpt` at session start via `command -v cpt`. If found, set `{cpt_cmd}` = `cpt`. If not, fall back to the direct script path and offer installation guidance.

* Good, because shorter commands reduce LLM token usage and transcription errors
* Good, because `pipx`-installed `cpt` embeds the correct Python interpreter — no `tomllib` / version issues
* Good, because standard Unix CLI pattern is familiar to both humans and LLMs
* Good, because zero regression — fallback path is the current behavior
* Good, because prompt has persistent dismissal — users are asked once, not repeatedly across sessions
* Neutral, because adds `{cpt_cmd}` and `{cpt_installed}` variables to track state
* Bad, because adds a `command -v` check at session start (sub-millisecond cost)

### Option 2: Always Use Direct Script Path

Keep the current SKILL.md approach. All agent invocations use `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py`.

* Good, because no changes needed — zero implementation cost
* Good, because no dependency on `cpt` being installed
* Bad, because long paths are error-prone for LLMs to reproduce accurately
* Bad, because relies on the correct `python3` version being on PATH (Python 3.11+ for `tomllib`)
* Bad, because does not look like a standard Unix tool — confusing for users reading agent output
* Bad, because misses the opportunity to use the existing `cpt` proxy that was designed for this purpose

### Option 3: Require cpt with No Fallback

Mandate `cpt` installation. SKILL.md only references `cpt`. Agent refuses to proceed if `cpt` is not on PATH.

* Good, because simplest agent instructions — always `cpt <command>`
* Good, because guarantees correct interpreter via `pipx`
* Bad, because breaks all environments where `cpt` is not installed — hard gate
* Bad, because CI environments and ephemeral containers may not have `pipx`
* Bad, because increases onboarding friction — users must install before any Cypilot work

## More Information

- Related: `cpt-cypilot-adr-pipx-distribution` (ADR-0003) — defines `pipx` as the installation mechanism for `cpt`
- Related: `cpt-cypilot-adr-proxy-cli-pattern` (ADR-0007) — defines the stateless proxy pattern that `cpt` implements
- The `cpt` proxy forwards all commands to the skill engine unchanged; there is zero behavioral difference between `cpt --json validate` and `python3 .../cypilot.py --json validate`

## Traceability

- **PRD**: [PRD.md](../PRD.md)
- **DESIGN**: [DESIGN.md](../DESIGN.md)

This decision directly addresses the following requirements and design elements:

* `cpt-cypilot-fr-core-installer` — extends the installer story to include agent-prompt integration, not just human installation
* `cpt-cypilot-fr-core-skill-engine` — the skill engine is invoked the same way regardless of entry point; this decision standardizes the agent-facing entry point
* `cpt-cypilot-principle-determinism-first` — deterministic CLI resolution at session start; no ambiguity about which interpreter or path is used
