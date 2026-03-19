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

## Prerequisite Checklist
- [ ] Agent has read SKILL.md
- [ ] Agent understands standalone vs inline workspace config
- [ ] Agent understands source roles and cross-repo traceability

## Phase 1: Discover
**Goal**: find candidate repos.

| Step | Action |
|---|---|
| Identify root | `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json info` |
| Scan nested repos | `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json workspace-init --dry-run` |
| Present results | show repo name/path, adapter found or not, and inferred role |
**Decision point**:
- [ ] User confirms which repos to include
- [ ] User chooses standalone workspace file vs inline config

## Phase 2: Configure
**Goal**: confirm workspace structure.
For each selected source, confirm `name`, relative `path` or `url`, `role`, and `adapter` (auto-discovered or explicit). Also confirm:
- `cross_repo` (default yes)
- `resolve_remote_ids` (default yes; both settings must be true to include remote IDs)
- workspace location: standalone `.cypilot-workspace.toml` or inline `[workspace]` in `config/core.toml`
Primary source is always determined by the current working directory; no `primary` field exists.

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

## Quick Reference

| Command | Purpose |
|---|---|
| `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json workspace-init [--root <dir>] [--output <path>] [--inline] [--force] [--dry-run]` | Scan and generate workspace config |
| `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json workspace-add --name <name> [--path <path> \| --url <url>] [--branch <branch>] [--role <role>] [--adapter <path>] [--inline] [--force]` | Add a source |
| `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json workspace-info` | Show workspace sources and status |
| `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json workspace-sync [--source <name>] [--dry-run] [--force]` | Fetch/update Git URL worktrees |
| `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json validate --local-only` | Disable cross-repo resolution |
| `python3 {cypilot_path}/.core/skills/cypilot/scripts/cypilot.py --json list-ids --source <name>` | Restrict IDs to one source |

## Next Steps
**After successful workspace setup**:
- Run `validate` from each participating repo to verify cross-repo ID resolution works
- Use `list-ids` to confirm artifacts from all sources are visible
- Add `source` fields to `artifacts.toml` entries that reference remote repos
- Consider adding workspace setup to project onboarding documentation
