---
cypilot: true
type: workflow
name: cypilot-workspace
description: Multi-repo workspace setup — discover repos, configure sources, generate workspace config, validate
version: 1.0
purpose: Guide workspace federation setup for cross-repo traceability
---

# Cypilot Workspace Workflow

<!-- toc -->

- [Overview](#overview)
- [Prerequisite Checklist](#prerequisite-checklist)
- [Phase 1: Discover](#phase-1-discover)
- [Phase 2: Configure](#phase-2-configure)
- [Phase 3: Generate](#phase-3-generate)
- [Phase 4: Validate](#phase-4-validate)
- [Quick Reference](#quick-reference)
- [Next Steps](#next-steps)

<!-- /toc -->

ALWAYS open and follow `{cypilot_path}/config/AGENTS.md` FIRST.
ALWAYS open and follow `{cypilot_path}/.gen/AGENTS.md` after config/AGENTS.md.
**Type**: Operation
**Role**: Any
**Output**: `.cypilot-workspace.toml` or inline `[workspace]` in `config/core.toml`

## Overview
Use this workflow to discover workspace sources, confirm roles/settings, write workspace config, and validate cross-repo traceability.

| User intent | Route |
|---|---|
| Create/configure workspace | `generate.md` → `workspace.md` |
| Check workspace status | `analyze.md` with workspace target |
Direct workspace quick commands skip Protocol Guard.

## Phase 1: Discover
**Goal**: find candidate repos.

| Step | Action |
|---|---|
| Identify root | `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json info` |
| Scan nested repos | `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json workspace-init --dry-run` |
| Present results | show repo name/path, adapter found or not, and inferred role |
**Decision point**: after presenting discovered repos, ask one explicit question that covers both inclusion and workspace location.

```text
Why this input is needed: choose which repositories become workspace sources and where the workspace config should live.
Reply with the selected repo numbers or names, then `standalone` or `inline`.
Suggested default: include reachable repos that have the expected adapter, and use `standalone` unless the user specifically wants workspace config inside `config/core.toml`.
- `standalone` → write `.cypilot-workspace.toml` and keep workspace config separate from `config/core.toml`.
- `inline` → write `[workspace]` inside `config/core.toml`.
```

## Phase 2: Configure
**Goal**: confirm workspace structure.
For each selected source, confirm `name`, relative `path` or `url`, `role`, and `adapter` (auto-discovered or explicit). Also confirm:
- `cross_repo` (default yes)
- `resolve_remote_ids` (default yes; both settings must be true to include remote IDs)
- workspace location: standalone `.cypilot-workspace.toml` or inline `[workspace]` in `config/core.toml`
Primary source is always determined by the current working directory; no `primary` field exists.

Use one batched confirmation prompt per source:

```text
Why this input is needed: confirm the exact source settings before writing workspace configuration.
Reply with `approve` to accept the proposed source settings, or list only the fields to change.
Suggested defaults: keep the detected `adapter`, keep `cross_repo = yes`, and keep `resolve_remote_ids = yes` unless the user wants stricter local-only behavior.
- `approve` → keep the proposed source settings and continue.
- field edits → update only the named fields, then re-show the proposal.
```

## Phase 3: Generate
**Goal**: write the workspace config.

| Action | Command |
|---|---|
| Initialize workspace | `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json workspace-init [--root <super-root>] [--output <path>] [--inline] [--force] [--dry-run]` |
| Add one source | `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json workspace-add --name <name> (--path <path> \| --url <url>) [--branch <branch>] [--role <role>] [--adapter <path>] [--inline]` |
`workspace-init` writes standalone config by default; `--inline` writes `[workspace]` into `config/core.toml`. `workspace-add` auto-detects workspace type unless `--inline` forces inline mode. Git URL sources are not supported inline.

## Phase 4: Validate
**Goal**: verify reachability, adapters, and cross-repo behavior.

| Check | Command / Expectation |
|---|---|
| Workspace status | `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json workspace-info` |
| Source health | path exists; adapter found if expected; `artifacts.toml` valid when adapter exists; at least one system if adapter exists |
| Cross-repo IDs | `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json list-ids` |
| Cross-repo validation | `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json validate` |
Report total sources, reachable sources, sources with adapters, and available cross-repo IDs.
**Graceful degradation**:
- missing repos emit warnings, not errors
- available sources continue working
- remote IDs from missing sources are unavailable
- explicit `source` entries targeting missing repos resolve to `None`
- scan failures warn on stderr without blocking the operation

## Next Steps
**After successful workspace setup**:
- Run `validate` from each participating repo to verify cross-repo ID resolution works
- Use `list-ids` to confirm artifacts from all sources are visible
- Add `source` fields to `artifacts.toml` entries that reference remote repos
- Consider adding workspace setup to project onboarding documentation

When presenting next steps to the user, include a suggested default and an explicit reply contract:

```text
What would you like to do next?
Reply with the option number or a short custom instruction.
1. Run `validate` from each participating repo — Suggested default; verifies cross-repo ID resolution end to end.
2. Run `list-ids` to confirm artifacts from all sources are visible.
3. Review or edit workspace/source fields before using the workspace further.
4. Other — describe the next workspace action you want.
```
