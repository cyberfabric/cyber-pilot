---
cypilot: true
type: requirement
name: Raw-Input Overflow Rule
version: 1.1
purpose: Shared overflow routing rule for analyze and generate workflows
---

# Raw-Input Overflow Rule

If the direct user prompt plus all provided files exceeds `500` total lines, the agent MUST NOT silently continue in direct workflow mode. It MUST present an explicit choice between `(a)` switching to `/cypilot-plan` or `(b)` continuing in the current direct workflow with reduced guarantees. If the user chooses `/cypilot-plan`, preserve the same request scope and require the planner to materialize that raw input under `{cypilot_path}/.plans/{task-slug}/input/` before decomposition. The planner MUST obtain explicit user approval before creating that directory or executing the write-capable `chunk-input` command shown below, and MUST pass `--include-stdin` when direct prompt text must be packaged together with provided files. If the user declines planning, the agent MAY continue in direct workflow mode only after explicitly warning that context overflow may reduce rule coverage, checklist coverage, or output quality. The explicit offer takes precedence over any later **single-context bypass check** (the Phase 1.2 estimate in `plan.md` that allows skipping plan compilation when the compiled estimate is `<= 500` lines): once the user accepts `/cypilot-plan` here, the planner MUST stay on the plan path even if that later check would otherwise allow a bypass.

Canonical write-capable invocation (executed only after explicit approval):

```
{cpt_cmd} --json chunk-input [<path> ...] --output-dir {cypilot_path}/.plans/{task-slug}/input [--include-stdin] [--stdin-label <label>] --max-lines 300 --threshold-lines 500
```

Read-only signature/reuse check (no files written, no approval required):

```
{cpt_cmd} --json chunk-input [<path> ...] --output-dir {cypilot_path}/.plans/{task-slug}/input [--include-stdin] --dry-run
```

Positional `<path>` arguments enumerate provided files (zero, one, or many); pass `--include-stdin` to additionally read direct prompt text from stdin alongside files; if no positional paths are given, the command reads stdin only (no `--include-stdin` needed) and the direct prompt is preserved as `direct-prompt.md` in the output directory.

**Applies to**: analyze workflow (direct analysis mode), generate workflow (direct generation mode).

**Plan workflow note**: when the raw task input itself exceeds `500` lines during planning and the user chooses to stay on the plan path, materialize it under `{cypilot_path}/.plans/{task-slug}/input/`, chunk it to `<= 300` lines per file, and treat the resulting chunk files as the authoritative raw-input package for the plan. Approval flow: the explicit user approval gate defined in the main requirement above (approval before creating the directory or running the write-capable `chunk-input` command) still applies inside the plan path — choosing `/cypilot-plan` selects the path but does not by itself authorize directory creation or chunking; the planner MUST request explicit confirmation immediately before the write-capable invocation.
