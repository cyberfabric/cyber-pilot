---
cypilot: true
type: requirement
name: Raw-Input Overflow Rule
version: 1.1
purpose: Shared overflow routing rule for analyze and generate workflows
---

# Raw-Input Overflow Rule

If the direct user prompt plus all provided files exceeds `500` total lines, the agent MUST NOT silently continue in direct workflow mode. It MUST present an explicit choice between `(a)` switching to `/cypilot-plan` or `(b)` continuing in the current direct workflow with reduced guarantees. If the user chooses `/cypilot-plan`, preserve the same request scope and require the planner to materialize that raw input under `{cypilot_path}/.plans/{task-slug}/input/` before decomposition. The planner MUST obtain explicit user approval before creating that directory or executing the write-capable `{cpt_cmd} --json chunk-input ... --max-lines 300 --threshold-lines 500` command, and MUST pass `--include-stdin` when direct prompt text must be packaged together with provided files. If the user declines planning, the agent MAY continue in direct workflow mode only after explicitly warning that context overflow may reduce rule coverage, checklist coverage, or output quality. The explicit offer takes precedence over any later single-context bypass check inside planning.

**Applies to**: analyze workflow (direct analysis mode), generate workflow (direct generation mode).

**Plan workflow note**: when the raw task input itself exceeds `500` lines during planning and the user chooses to stay on the plan path, materialize it under `{cypilot_path}/.plans/{task-slug}/input/`, chunk it to `<= 300` lines per file, and treat the resulting chunk files as the authoritative raw-input package for the plan.
